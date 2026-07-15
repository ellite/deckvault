<script lang="ts">
  interface Props {
    storageMediumId: number;
    onClose: () => void;
    onAdded: (game: any) => void;
    showToast: (msg: string, type?: "success" | "error") => void;
  }
  import { onMount } from "svelte";
  let { storageMediumId, onClose, onAdded, showToast }: Props = $props();

  let searchInput: HTMLInputElement;
  onMount(() => searchInput?.focus());

  let query = $state("");
  let results: any[] = $state([]);
  let selected: any = $state(null);
  let searching = $state(false);
  let adding = $state(false);
  let error = $state("");
  let searchTimeout: ReturnType<typeof setTimeout>;

  function onQueryInput() {
    clearTimeout(searchTimeout);
    if (query.length < 2) { results = []; return; }
    searchTimeout = setTimeout(doSearch, 400);
  }

  async function doSearch() {
    searching = true; error = "";
    try {
      const res = await fetch(`/api/igdb/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Search failed");
      results = await res.json();
    } catch (e: any) {
      error = e.message;
    } finally {
      searching = false;
    }
  }

  async function addGame() {
    const payload = selected ?? { title: query.trim() };
    if (!payload.title) { error = "Enter a game name"; return; }
    adding = true; error = "";
    try {
      const res = await fetch(`/api/storage/${storageMediumId}/games`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail ?? "Failed to add");
      }
      const game = await res.json();
      showToast(`"${game.title}" added!`);
      onAdded(game);
      onClose();
    } catch (e: any) {
      error = e.message;
    } finally {
      adding = false;
    }
  }

  function selectGame(g: any) {
    selected = g;
    query = g.title;
    results = [];
  }

  function backdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) onClose();
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4"
  onmousedown={backdrop}
>
  <div class="card w-full max-w-xl p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold">Add Game</h2>
      <button class="btn-ghost p-1.5" onclick={onClose} aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Search -->
    <div>
      <label class="label" for="game-search">Search IGDB</label>
      <div class="relative">
        <input
          id="game-search"
          class="input pr-10"
          bind:value={query}
          bind:this={searchInput}
          oninput={onQueryInput}
          placeholder="Type a game name…"
          autocomplete="off"
        />
        {#if searching}
          <div class="absolute right-3 top-1/2 -translate-y-1/2">
            <svg class="animate-spin w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
          </div>
        {/if}
      </div>

      <!-- Results: inline so they push the card up on mobile instead of going under the keyboard -->
      {#if results.length > 0}
        <div class="mt-1 w-full bg-white dark:bg-surface-dark border border-border dark:border-border-dark rounded-xl shadow-xl overflow-y-auto max-h-[45dvh] sm:max-h-60">
          {#each results as g}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <div
              role="option"
              aria-selected={selected?.igdb_id === g.igdb_id}
              class="flex items-center gap-3 p-3 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors"
              onclick={() => selectGame(g)}
            >
              {#if g.cover_url}
                <img src={g.cover_url} alt={g.title} class="w-10 h-14 object-cover rounded-lg flex-shrink-0" />
              {:else}
                <div class="w-10 h-14 bg-slate-100 dark:bg-white/10 rounded-lg flex-shrink-0 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
                  </svg>
                </div>
              {/if}
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-sm truncate">{g.title}</p>
                <p class="text-xs text-slate-400 dark:text-slate-500">
                  {g.release_year ?? "Unknown year"}
                  {g.genres ? ` · ${g.genres}` : ""}
                </p>
                {#if g.rating}
                  <p class="text-xs text-amber-500 font-semibold mt-0.5">★ {g.rating}/100</p>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Selected game preview -->
    {#if selected}
      <div class="flex gap-4 p-4 bg-primary/5 dark:bg-primary/10 rounded-xl border border-primary/20">
        {#if selected.cover_url}
          <img src={selected.cover_url} alt={selected.title} class="w-16 h-22 object-cover rounded-lg flex-shrink-0" />
        {/if}
        <div class="flex-1 min-w-0">
          <p class="font-bold">{selected.title}</p>
          {#if selected.genres}
            <p class="text-xs text-slate-400 mt-0.5">{selected.genres}</p>
          {/if}
          {#if selected.release_year}
            <p class="text-xs text-slate-400">{selected.release_year}</p>
          {/if}
          {#if selected.summary}
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">{selected.summary}</p>
          {/if}
        </div>
        <button
          class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 flex-shrink-0 self-start"
          onclick={() => { selected = null; }}
          aria-label="Clear selection"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    {/if}

    {#if !selected && query.trim().length > 0}
      <p class="text-xs text-slate-400 dark:text-slate-500">
        Can't find it? <button class="underline text-primary" onclick={addGame}>Add "{query}" manually</button>
      </p>
    {/if}

    {#if error}
      <p class="text-sm text-red-500">{error}</p>
    {/if}

    <div class="flex gap-3 pt-1">
      <button class="btn-ghost flex-1" onclick={onClose}>Cancel</button>
      <button class="btn-primary flex-1" onclick={addGame} disabled={adding || (!selected && !query.trim())}>
        {adding ? "Adding…" : "Add Game"}
      </button>
    </div>
  </div>
</div>
