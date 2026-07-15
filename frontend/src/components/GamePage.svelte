<script lang="ts">
  import { onMount } from "svelte";
  import ConfirmDialog from "./ConfirmDialog.svelte";

  interface InstallInfo {
    game_id: number; storage_id: number;
    storage_label: string; storage_type: string; storage_color: string;
  }
  interface Game {
    id: number; title: string; cover_url?: string; genres?: string;
    release_year?: number; rating?: number; summary?: string;
    storage_medium_id: number; other_installations: InstallInfo[];
  }
  interface StorageMedium {
    id: number; type: string; label: string; color: string;
  }
  interface Props { game: Game; storage: StorageMedium; }
  let { game, storage }: Props = $props();

  let deleting = $state(false);
  let showConfirm = $state(false);
  let backHref = $state(`/storage/${storage.id}`);
  let backLabel = $state(storage.label);

  onMount(() => {
    const from = new URLSearchParams(window.location.search).get("from");
    if (from === "library") {
      backHref = "/library";
      backLabel = "Library";
    }
  });

  function typeLabel(type: string) {
    const map: Record<string, string> = { local: "Internal", sdcard: "SD Card", hdd: "HDD", ssd: "SSD" };
    return map[type] ?? type;
  }

  const genres = $derived(
    game.genres ? game.genres.split(",").map((g) => g.trim()).filter(Boolean) : []
  );

  async function removeFromLibrary() {
    deleting = true;
    try {
      const res = await fetch(`/api/games/${game.id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed");
      window.location.href = `/storage/${storage.id}`;
    } catch {
      deleting = false;
    }
  }
</script>

<div class="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
  <!-- Breadcrumb -->
  <a href={backHref}
     class="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors mb-6">
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
    </svg>
    {backLabel}
  </a>

  <!-- Game hero -->
  <div class="flex flex-col sm:flex-row gap-6 sm:gap-8">
    <!-- Cover art -->
    <div class="flex-shrink-0 w-36 sm:w-48 mx-auto sm:mx-0">
      {#if game.cover_url}
        <img src={game.cover_url} alt={game.title}
             class="w-full rounded-2xl shadow-2xl ring-1 ring-black/10 dark:ring-white/10" />
      {:else}
        <div class="w-full aspect-[3/4] rounded-2xl bg-slate-100 dark:bg-white/5
                    flex items-center justify-center ring-1 ring-border dark:ring-border-dark">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 text-slate-300 dark:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
          </svg>
        </div>
      {/if}
    </div>

    <!-- Details -->
    <div class="flex-1 min-w-0">
      <h1 class="text-2xl sm:text-3xl font-bold leading-tight">{game.title}</h1>

      <!-- Metadata chips -->
      <div class="flex flex-wrap gap-2 mt-3">
        {#if game.release_year}
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300">
            {game.release_year}
          </span>
        {/if}
        {#if game.rating}
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400">
            ★ {Math.round(game.rating)}/100
          </span>
        {/if}
        {#each genres as genre}
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary-light">
            {genre}
          </span>
        {/each}
      </div>

      {#if game.summary}
        <p class="mt-5 text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          {game.summary}
        </p>
      {/if}

      <!-- Storage info -->
      <div class="mt-6 pt-6 border-t border-border dark:border-border-dark">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
          Installed on
        </p>
        <div class="flex flex-col gap-2">
          <!-- This copy -->
          <a href="/storage/{storage.id}"
             class="inline-flex items-center gap-2.5 hover:opacity-75 transition-opacity w-fit">
            <span class="w-3 h-3 rounded-full flex-shrink-0" style="background:{storage.color}"></span>
            <span class="font-semibold">{storage.label}</span>
            <span class="text-xs text-slate-400 dark:text-slate-500">{typeLabel(storage.type)}</span>
          </a>
          <!-- Other copies of the same game -->
          {#each game.other_installations as install}
            <a href="/games/{install.game_id}{backHref === '/library' ? '?from=library' : ''}"
               class="inline-flex items-center gap-2.5 hover:opacity-75 transition-opacity w-fit">
              <span class="w-3 h-3 rounded-full flex-shrink-0" style="background:{install.storage_color}"></span>
              <span class="font-semibold">{install.storage_label}</span>
              <span class="text-xs text-slate-400 dark:text-slate-500">{typeLabel(install.storage_type)}</span>
            </a>
          {/each}
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex gap-3">
        <a href={backHref} class="btn-ghost text-sm">← {backLabel}</a>
        <button class="btn-danger text-sm" onclick={() => showConfirm = true} disabled={deleting}>
          {deleting ? "Removing…" : "Remove from Library"}
        </button>
      </div>
    </div>
  </div>
</div>

{#if showConfirm}
  <ConfirmDialog
    title="Remove game"
    message={`Remove "${game.title}" from ${storage.label}? This won't affect other installs.`}
    confirmLabel="Remove"
    onConfirm={() => { showConfirm = false; removeFromLibrary(); }}
    onCancel={() => showConfirm = false}
  />
{/if}
