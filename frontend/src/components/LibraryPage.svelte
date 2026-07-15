<script lang="ts">
  interface InstallInfo {
    game_id: number;
    storage_id: number;
    storage_label: string;
    storage_type: string;
    storage_color: string;
  }
  interface LibraryEntry {
    igdb_id: number | null;
    title: string;
    cover_url: string | null;
    genres: string | null;
    release_year: number | null;
    rating: number | null;
    summary: string | null;
    installations: InstallInfo[];
    is_duplicate: boolean;
  }
  interface Props { entries: LibraryEntry[]; }
  let { entries }: Props = $props();

  let search = $state("");
  let duplicatesOnly = $state(false);

  const totalGames = $derived(entries.length);
  const duplicateCount = $derived(entries.filter((e) => e.is_duplicate).length);

  const filtered = $derived(
    entries
      .filter((e) => !duplicatesOnly || e.is_duplicate)
      .filter((e) => !search.trim() || e.title.toLowerCase().includes(search.trim().toLowerCase()))
  );

  function typeLabel(type: string) {
    const map: Record<string, string> = { local: "Internal", sdcard: "SD Card", hdd: "HDD", ssd: "SSD" };
    return map[type] ?? type;
  }
</script>

<div class="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
  <!-- Header -->
  <div class="mb-6">
    <h1 class="text-2xl font-bold">Library</h1>
    <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
      {totalGames} {totalGames === 1 ? "game" : "games"}
      {#if duplicateCount > 0}
        · {duplicateCount} on multiple devices
      {/if}
    </p>
  </div>

  <!-- Search + filter -->
  <div class="flex gap-3 mb-6">
    <div class="relative flex-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input
        class="input pl-9"
        bind:value={search}
        placeholder="Search games…"
        type="search"
      />
    </div>
    {#if duplicateCount > 0}
      <button
        onclick={() => duplicatesOnly = !duplicatesOnly}
        class="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-xl border-2 text-sm font-semibold transition-colors
               {duplicatesOnly
                 ? 'border-amber-400 bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300'
                 : 'border-border dark:border-border-dark text-slate-500 dark:text-slate-400 hover:border-amber-300 dark:hover:border-amber-500/40'}"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        </svg>
        Duplicates
      </button>
    {/if}
  </div>

  <!-- Empty states -->
  {#if entries.length === 0}
    <div class="flex flex-col items-center justify-center min-h-[50vh] text-center">
      <div class="w-20 h-20 rounded-2xl bg-primary/10 dark:bg-primary/20 flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
        </svg>
      </div>
      <h2 class="text-xl font-bold mb-2">No games yet</h2>
      <p class="text-slate-500 dark:text-slate-400 max-w-xs">
        Add games to your storage mediums and they'll appear here.
      </p>
    </div>

  {:else if filtered.length === 0}
    <div class="text-center py-16 text-slate-400 dark:text-slate-500">
      <p class="font-medium">No games match "{search}"</p>
    </div>

  {:else}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
      {#each filtered as entry}
        <div class="card overflow-hidden group relative flex flex-col {entry.is_duplicate ? 'ring-1 ring-amber-400/60 dark:ring-amber-400/40' : ''}">
          <!-- Duplicate badge -->
          {#if entry.is_duplicate}
            <div class="absolute top-2 left-2 z-10 flex items-center gap-1 bg-amber-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md shadow">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01"/>
              </svg>
              ×{entry.installations.length}
            </div>
          {/if}

          <!-- Cover art - always a link; game page shows all installations -->
          <a href="/games/{entry.installations[0].game_id}?from=library" class="block aspect-[3/4] bg-slate-100 dark:bg-white/5 relative flex-shrink-0">
            {#if entry.cover_url}
              <img src={entry.cover_url} alt={entry.title} class="w-full h-full object-cover" loading="lazy" />
            {:else}
              <div class="w-full h-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-slate-300 dark:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
                </svg>
              </div>
            {/if}
            {#if entry.rating}
              <span class="absolute bottom-1.5 right-1.5 bg-black/60 backdrop-blur-sm text-amber-400 text-xs font-bold px-1.5 py-0.5 rounded-md">
                ★ {Math.round(entry.rating)}
              </span>
            {/if}
          </a>

          <!-- Info + installs -->
          <div class="p-2.5 flex flex-col gap-2 flex-1">
            <div>
              <p class="text-xs font-semibold leading-snug line-clamp-2">{entry.title}</p>
              {#if entry.release_year}
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{entry.release_year}</p>
              {/if}
            </div>

            <!-- Installation chips - each links to that specific game record -->
            <div class="flex flex-col gap-1 mt-auto">
              {#each entry.installations as install}
                <a
                  href="/games/{install.game_id}?from=library"
                  class="flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-medium
                         bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10
                         transition-colors leading-none truncate"
                  title="{install.storage_label} · {typeLabel(install.storage_type)}"
                >
                  <span class="w-2 h-2 rounded-full flex-shrink-0" style="background:{install.storage_color}"></span>
                  <span class="truncate">{install.storage_label}</span>
                </a>
              {/each}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
