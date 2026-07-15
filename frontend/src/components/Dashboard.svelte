<script lang="ts">
  import { onMount } from "svelte";
  import AddStorageModal from "./AddStorageModal.svelte";
  import Toast from "./Toast.svelte";

  interface Game { id: number; }
  interface StorageMedium {
    id: number; type: string; label: string; brand?: string; model?: string;
    size_gb?: number; free_gb?: number; notes?: string; color: string;
    color_primary?: string; color_secondary?: string; games: Game[];
  }
  interface Props { initialStorage: StorageMedium[]; }
  let { initialStorage }: Props = $props();

  let storageList: StorageMedium[] = $state(initialStorage);
  let showAddStorage = $state(false);
  let showSortMenu = $state(false);
  let toast: Toast;

  type SortMode = "type" | "total" | "used" | "free" | "games";
  const VALID_SORTS: SortMode[] = ["type", "total", "used", "free", "games"];
  let sort = $state<SortMode>("type");

  onMount(() => {
    const saved = localStorage.getItem("dv-sort") as SortMode;
    if (saved && VALID_SORTS.includes(saved)) sort = saved;
  });

  $effect(() => {
    localStorage.setItem("dv-sort", sort);
  });

  const SORT_OPTIONS: { value: SortMode; label: string }[] = [
    { value: "type",  label: "Type" },
    { value: "total", label: "Total" },
    { value: "used",  label: "Used" },
    { value: "free",  label: "Available" },
    { value: "games", label: "Games" },
  ];

  const TYPE_ORDER: Record<string, number> = { local: 0, sdcard: 1, hdd: 2, ssd: 3 };
  const TYPE_LABELS: Record<string, string> = {
    local: "Internal Storage",
    sdcard: "SD Cards",
    hdd: "Hard Drives",
    ssd: "SSDs",
  };

  function usedGb(s: StorageMedium) {
    if (s.size_gb == null) return -1;
    return s.size_gb - (s.free_gb ?? 0);
  }

  function usedPct(s: StorageMedium) {
    if (!s.size_gb || s.free_gb == null) return null;
    return Math.round(((s.size_gb - s.free_gb) / s.size_gb) * 100);
  }

  function fmtSize(gb: number) {
    return gb >= 1000 ? `${(gb / 1000).toFixed(1)} TB` : `${gb} GB`;
  }

  function typeLabel(type: string) {
    const map: Record<string, string> = { local: "Internal", sdcard: "SD Card", hdd: "HDD", ssd: "SSD" };
    return map[type] ?? type;
  }

  const sorted = $derived.by(() => {
    const list = [...storageList];
    if (sort === "type") {
      list.sort((a, b) => {
        const td = (TYPE_ORDER[a.type] ?? 99) - (TYPE_ORDER[b.type] ?? 99);
        return td !== 0 ? td : a.label.localeCompare(b.label);
      });
    } else if (sort === "total") {
      list.sort((a, b) => (b.size_gb ?? -1) - (a.size_gb ?? -1));
    } else if (sort === "used") {
      list.sort((a, b) => usedGb(b) - usedGb(a));
    } else if (sort === "free") {
      list.sort((a, b) => (b.free_gb ?? -1) - (a.free_gb ?? -1));
    } else if (sort === "games") {
      list.sort((a, b) => b.games.length - a.games.length);
    }
    return list;
  });

  const groups = $derived.by(() => {
    if (sort !== "type") return null;
    const map = new Map<string, StorageMedium[]>();
    for (const s of sorted) {
      if (!map.has(s.type)) map.set(s.type, []);
      map.get(s.type)!.push(s);
    }
    return [...map.entries()].map(([type, items]) => ({
      type,
      label: TYPE_LABELS[type] ?? type,
      items,
    }));
  });

  function onStorageCreated(medium: any) {
    window.location.href = `/storage/${medium.id}`;
  }
</script>

<Toast bind:this={toast} />

{#snippet card(s: StorageMedium)}
  {@const pct = usedPct(s)}
  <a href="/storage/{s.id}"
     class="card group block overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-150 no-underline">
    <div class="h-1.5 w-full" style="background:{s.color}"></div>
    <div class="p-4 sm:p-5">
      <div class="flex items-start justify-between gap-2 mb-3">
        <div class="min-w-0">
          <h2 class="font-bold text-base leading-snug truncate">{s.label}</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">
            {[s.brand, s.model].filter(Boolean).join(" · ") || " "}
          </p>
        </div>
        <span class="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold"
              style="background:{s.color}22; color:{s.color}">
          {typeLabel(s.type)}
        </span>
      </div>

      {#if s.size_gb}
        <div class="mb-3">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1.5">
            {#if pct !== null}
              <span>{fmtSize(s.size_gb - (s.free_gb ?? 0))} used</span>
              <span>{fmtSize(s.free_gb!)} free</span>
            {:else}
              <span>{fmtSize(s.size_gb)}</span>
            {/if}
          </div>
          <div class="w-full h-1.5 rounded-full bg-slate-100 dark:bg-white/10 overflow-hidden">
            {#if pct !== null}
              <div class="h-full rounded-full" style="width:{pct}%; background:{s.color}; opacity:0.85"></div>
            {:else}
              <div class="h-full rounded-full w-full" style="background:{s.color}; opacity:0.25"></div>
            {/if}
          </div>
        </div>
      {/if}

      <div class="flex items-center justify-between mt-3 pt-3 border-t border-border dark:border-border-dark">
        <div class="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
          </svg>
          <span class="text-sm font-medium">{s.games.length} {s.games.length === 1 ? "game" : "games"}</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:group-hover:text-slate-300 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </div>
    </div>
  </a>
{/snippet}

<div class="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold">Storage</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
        {storageList.length} {storageList.length === 1 ? "medium" : "mediums"}
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if storageList.length > 1}
        <div class="relative">
          <button
            onclick={() => showSortMenu = !showSortMenu}
            class="flex items-center gap-1.5 px-4 py-2 rounded-xl font-medium
                   border border-border dark:border-border-dark
                   hover:bg-slate-50 dark:hover:bg-white/5 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/>
            </svg>
            {SORT_OPTIONS.find((o) => o.value === sort)?.label}
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-slate-400 transition-transform {showSortMenu ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          {#if showSortMenu}
            <div class="fixed inset-0 z-10" onclick={() => showSortMenu = false}></div>
            <div class="absolute right-0 top-full mt-1.5 z-20 w-44 card shadow-xl py-1 overflow-hidden">
              {#each SORT_OPTIONS as opt}
                <button
                  onclick={() => { sort = opt.value; showSortMenu = false; }}
                  class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-left transition-colors
                         hover:bg-slate-50 dark:hover:bg-white/5
                         {sort === opt.value
                           ? 'text-primary dark:text-primary-light font-semibold'
                           : 'text-slate-700 dark:text-slate-300'}"
                >
                  {#if sort === opt.value}
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                    </svg>
                  {:else}
                    <span class="w-3.5"></span>
                  {/if}
                  {opt.label}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      {/if}

      <button class="btn-primary flex items-center gap-1.5" onclick={() => showAddStorage = true}>
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add Storage
      </button>
    </div>
  </div>

  {#if storageList.length === 0}
    <div class="flex flex-col items-center justify-center min-h-[55vh] text-center">
      <div class="w-20 h-20 rounded-2xl bg-primary/10 dark:bg-primary/20 flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
        </svg>
      </div>
      <h2 class="text-xl font-bold mb-2">No storage yet</h2>
      <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-xs">
        Add your internal storage, SD cards, or external drives to start tracking your library.
      </p>
      <button class="btn-primary" onclick={() => showAddStorage = true}>Add Storage Medium</button>
    </div>

  {:else if groups}
    <!-- Grouped by type with section headings -->
    {#each groups as group, i}
      <div class={i > 0 ? "mt-8" : ""}>
        <div class="flex items-center gap-3 mb-4">
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 whitespace-nowrap">
            {group.label}
          </h2>
          <div class="flex-1 h-px bg-border dark:bg-border-dark"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">{group.items.length}</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {#each group.items as s}
            {@render card(s)}
          {/each}
        </div>
      </div>
    {/each}

  {:else}
    <!-- Flat sorted grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {#each sorted as s}
        {@render card(s)}
      {/each}
    </div>
  {/if}
</div>

{#if showAddStorage}
  <AddStorageModal
    onClose={() => showAddStorage = false}
    onCreated={onStorageCreated}
    showToast={(m, t) => toast.show(m, t)}
  />
{/if}
