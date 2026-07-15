<script lang="ts">
  import AddGameModal from "./AddGameModal.svelte";
  import EditStorageModal from "./EditStorageModal.svelte";
  import ConfirmDialog from "./ConfirmDialog.svelte";
  import Toast from "./Toast.svelte";

  interface Game {
    id: number; title: string; cover_url?: string; genres?: string;
    release_year?: number; rating?: number; summary?: string;
  }
  interface StorageMedium {
    id: number; type: string; label: string; brand?: string; model?: string;
    size_gb?: number; free_gb?: number; notes?: string; color: string;
    color_primary?: string; color_secondary?: string; games: Game[];
  }
  interface Props { storage: StorageMedium; }
  let { storage }: Props = $props();

  let games: Game[] = $state(storage.games ?? []);
  let showAddGame = $state(false);
  let showEditStorage = $state(false);
  let deletingGame: number | null = $state(null);
  let deletingStorage = $state(false);
  let toast: Toast;
  let confirmGameId: number | null = $state(null);
  let confirmDeleteStorage = $state(false);

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

  function onGameAdded(game: Game) {
    games = [...games, game];
  }

  async function deleteGame(gameId: number) {
    deletingGame = gameId;
    try {
      const res = await fetch(`/api/games/${gameId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed");
      games = games.filter((g) => g.id !== gameId);
      toast.show("Game removed");
    } catch {
      toast.show("Failed to remove game", "error");
    } finally {
      deletingGame = null;
    }
  }

  async function deleteStorage() {
    deletingStorage = true;
    try {
      const res = await fetch(`/api/storage/${storage.id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed");
      window.location.href = "/storage";
    } catch {
      toast.show("Failed to delete storage", "error");
      deletingStorage = false;
    }
  }

  const pct = $derived(usedPct(storage));
</script>

<Toast bind:this={toast} />

<div class="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto">
  <!-- Breadcrumb -->
  <a href="/storage"
     class="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors mb-6">
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
    </svg>
    All Storage
  </a>

  <!-- Header: graphic + info -->
  <div class="flex flex-col lg:flex-row gap-6 lg:gap-10 mb-10">
    <!-- Device graphic -->
    {#if storage.type === "sdcard"}
      {@const cp = storage.color_primary ?? "#dc2626"}
      {@const cs = storage.color_secondary ?? "#1c1c2e"}
      {@const uid = `sd-${storage.id}`}
      <div class="flex-shrink-0 w-full max-w-xs mx-auto lg:mx-0 lg:w-72">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 270 172" class="w-full drop-shadow-2xl">
          <defs>
            <clipPath id="body-{uid}">
              <path d="M 40 4 L 258 4 Q 268 4 268 14 L 268 158 Q 268 168 258 168 L 12 168 Q 2 168 2 158 L 2 44 Z"/>
            </clipPath>
            <filter id="shadow-{uid}">
              <feDropShadow dx="0" dy="5" stdDeviation="8" flood-opacity="0.4"/>
            </filter>
            <linearGradient id="sheen-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="white" stop-opacity="0.16"/>
              <stop offset="70%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path d="M 40 4 L 258 4 Q 268 4 268 14 L 268 158 Q 268 168 258 168 L 12 168 Q 2 168 2 158 L 2 44 Z"
                fill="rgba(0,0,0,0.45)" filter="url(#shadow-{uid})" transform="translate(2,5)"/>
          <g clip-path="url(#body-{uid})">
            <rect x="0" y="0" width="268" height="70" fill={cp}/>
            <rect x="0" y="70" width="268" height="172" fill={cs}/>
            <line x1="2" y1="70" x2="268" y2="70" stroke="rgba(0,0,0,0.22)" stroke-width="1.5"/>
            <rect x="0" y="0" width="268" height="172" fill="url(#sheen-{uid})"/>
            {#if storage.brand}
              <text x="135" y="32" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="13" font-weight="800" letter-spacing="2" fill="white" opacity="0.95">{storage.brand.toUpperCase()}</text>
            {/if}
            <text x="135" y={storage.brand ? 56 : 44} text-anchor="middle" font-family="system-ui,-apple-system,sans-serif"
                  font-size={storage.model && storage.model.length > 10 ? 13 : 17} font-weight="700" font-style="italic" fill="white" opacity="0.88">
              {storage.model || storage.label}
            </text>
            {#if storage.size_gb}
              <text x="135" y="118" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="40" font-weight="800" fill="white" opacity="0.95">{fmtSize(storage.size_gb)}</text>
            {/if}
            {#if storage.free_gb != null}
              <text x="135" y="140" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="11" fill="white" opacity="0.6">{fmtSize(storage.free_gb)} free</text>
            {/if}
            {#if pct !== null}
              <rect x="68" y="150" width="130" height="5" rx="2.5" fill="rgba(255,255,255,0.2)"/>
              <rect x="68" y="150" width={Math.round(130 * pct / 100)} height="5" rx="2.5" fill="white" opacity="0.7"/>
            {/if}
          </g>
          <path d="M 40 4 L 2 44 L 2 4 Z" fill="rgba(0,0,0,0.3)"/>
          <path d="M 40 4 L 2 44" stroke="rgba(255,255,255,0.08)" stroke-width="1" fill="none"/>
        </svg>
      </div>

    {:else if storage.type === "hdd"}
      {@const uid = `hdd-${storage.id}`}
      <div class="flex-shrink-0 w-full max-w-xs mx-auto lg:mx-0 lg:w-72">
        <svg viewBox="0 0 296 172" class="w-full drop-shadow-2xl" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="metal-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#d1d5db"/><stop offset="100%" stop-color="#9ca3af"/>
            </linearGradient>
            <linearGradient id="sheen-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="white" stop-opacity="0.2"/><stop offset="100%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
            <filter id="sh-{uid}"><feDropShadow dx="0" dy="5" stdDeviation="8" flood-opacity="0.4"/></filter>
          </defs>
          <rect x="4" y="8" width="274" height="158" rx="10" fill="black" opacity="0.3" filter="url(#sh-{uid})"/>
          <rect x="0" y="0" width="274" height="158" rx="10" fill="url(#metal-{uid})"/>
          <rect x="256" y="42" width="20" height="74" rx="3" fill="#6b7280"/>
          <rect x="258" y="46" width="15" height="30" rx="1.5" fill="#4b5563"/>
          {#each [0,1,2,3,4,5,6] as i}
            <rect x="259" y={48 + i*3.8} width="11" height="2.2" rx="0.5" fill="#c9a227" opacity="0.9"/>
          {/each}
          <rect x="258" y="80" width="15" height="30" rx="1.5" fill="#374151"/>
          {#each [0,1,2,3,4,5,6,7,8,9,10,11,12,13] as i}
            <rect x="259" y={82 + i*1.9} width="11" height="1.2" rx="0.3" fill="#c9a227" opacity="0.75"/>
          {/each}
          <rect x="6" y="6" width="244" height="146" rx="8" fill={storage.color} opacity="0.9"/>
          <rect x="6" y="6" width="244" height="73" rx="8" fill="url(#sheen-{uid})"/>
          <g opacity="0.13">
            <circle cx="72" cy="79" r="54" fill="none" stroke="white" stroke-width="1.5"/>
            <circle cx="72" cy="79" r="38" fill="none" stroke="white" stroke-width="1.5"/>
            <circle cx="72" cy="79" r="22" fill="none" stroke="white" stroke-width="1.5"/>
            <circle cx="72" cy="79" r="7" fill="white"/>
          </g>
          <path d="M 72 79 L 114 48" stroke="rgba(255,255,255,0.22)" stroke-width="5" stroke-linecap="round"/>
          <circle cx="114" cy="48" r="6" fill="rgba(255,255,255,0.18)"/>
          {#if storage.brand}
            <text x="178" y="54" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="800" letter-spacing="1.5" fill="white" opacity="0.95">{storage.brand.toUpperCase()}</text>
          {/if}
          <text x="178" y={storage.brand ? 74 : 64} text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="white" opacity="0.75">{storage.model || storage.label}</text>
          {#if storage.size_gb}
            <text x="178" y="114" text-anchor="middle" font-family="system-ui,sans-serif" font-size="36" font-weight="800" fill="white" opacity="0.95">{fmtSize(storage.size_gb)}</text>
          {/if}
          {#if storage.free_gb != null}
            <text x="178" y="135" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="white" opacity="0.6">{fmtSize(storage.free_gb)} free</text>
          {/if}
          {#if pct !== null}
            <rect x="110" y="143" width="130" height="4" rx="2" fill="rgba(255,255,255,0.2)"/>
            <rect x="110" y="143" width={Math.round(130 * pct / 100)} height="4" rx="2" fill="white" opacity="0.7"/>
          {/if}
          {#each [[10,10],[262,10],[10,148],[262,148],[10,79],[262,79]] as [sx,sy]}
            <circle cx={sx} cy={sy} r="6" fill="rgba(0,0,0,0.28)"/>
            <circle cx={sx} cy={sy} r="3.5" fill="rgba(0,0,0,0.35)"/>
            <line x1={sx-2} y1={sy} x2={sx+2} y2={sy} stroke="rgba(80,80,80,0.8)" stroke-width="0.8"/>
            <line x1={sx} y1={sy-2} x2={sx} y2={sy+2} stroke="rgba(80,80,80,0.8)" stroke-width="0.8"/>
          {/each}
        </svg>
      </div>

    {:else if storage.type === "ssd"}
      {@const uid = `ssd-${storage.id}`}
      {@const pcb = storage.color_primary ?? "#15803d"}
      <div class="flex-shrink-0 w-full max-w-sm mx-auto lg:mx-0 lg:w-80">
        <svg viewBox="0 0 340 108" class="w-full drop-shadow-2xl" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="pcb-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="{pcb}" stop-opacity="1"/>
              <stop offset="100%" stop-color="{pcb}" stop-opacity="0.75"/>
            </linearGradient>
            <linearGradient id="sheen-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="white" stop-opacity="0.12"/><stop offset="100%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
            <filter id="sh-{uid}"><feDropShadow dx="0" dy="5" stdDeviation="8" flood-opacity="0.4"/></filter>
          </defs>
          <rect x="4" y="8" width="328" height="94" rx="6" fill="black" opacity="0.3" filter="url(#sh-{uid})"/>
          <rect x="0" y="0" width="328" height="94" rx="5" fill="url(#pcb-{uid})"/>
          <g stroke="rgba(255,255,255,0.06)" stroke-width="1" fill="none">
            <line x1="60" y1="0" x2="60" y2="94"/><line x1="120" y1="0" x2="120" y2="94"/>
            <line x1="180" y1="0" x2="180" y2="94"/><line x1="240" y1="0" x2="240" y2="94"/>
            <line x1="0" y1="32" x2="328" y2="32"/><line x1="0" y1="62" x2="328" y2="62"/>
          </g>
          <rect x="0" y="0" width="328" height="94" rx="5" fill="url(#sheen-{uid})"/>
          <rect x="306" y="0" width="22" height="94" rx="0 5 5 0" fill="#374151"/>
          <rect x="304" y="0" width="2" height="94" fill="rgba(0,0,0,0.3)"/>
          <rect x="306" y="28" width="22" height="12" fill="#1f2937"/>
          {#each [4,9,14,19,34,39,44,49,54,59,64,69,74,79] as py}
            <rect x="308" y={py} width="16" height="4" rx="0.5" fill="#c9a227" opacity="0.95"/>
          {/each}
          {#each [[12,8],[12,52],[78,8],[78,52],[144,8],[144,52]] as [cx,cy]}
            <rect x={cx} y={cy} width="58" height="34" rx="3" fill="rgba(0,0,0,0.55)"/>
            <rect x={cx+2} y={cy+2} width="54" height="30" rx="2" fill="rgba(0,0,0,0.35)"/>
            <circle cx={cx+7} cy={cy+7} r="3" fill="rgba(255,255,255,0.2)"/>
          {/each}
          <rect x="218" y="14" width="72" height="60" rx="4" fill="rgba(0,0,0,0.6)"/>
          <rect x="220" y="16" width="68" height="56" rx="3" fill="rgba(0,0,0,0.4)"/>
          <circle cx="228" cy="24" r="3.5" fill="rgba(255,255,255,0.18)"/>
          {#if storage.brand}
            <text x="254" y="44" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" font-weight="700" letter-spacing="0.5" fill="rgba(255,255,255,0.6)">{storage.brand}</text>
          {/if}
          {#if storage.size_gb}
            <text x="254" y="60" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="800" fill="rgba(255,255,255,0.7)">{fmtSize(storage.size_gb)}</text>
          {/if}
          <circle cx="12" cy="47" r="6" fill="rgba(0,0,0,0.5)"/>
          <circle cx="12" cy="47" r="3.5" fill="rgba(0,0,0,0.6)"/>
        </svg>
      </div>

    {:else}
      <!-- Internal Storage: Steam Deck handheld -->
      {@const uid = `local-${storage.id}`}
      {@const ac = storage.color}
      <div class="flex-shrink-0 w-full max-w-sm mx-auto lg:mx-0 lg:w-80">
        <svg viewBox="0 0 340 210" class="w-full drop-shadow-2xl" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="body-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#2d2d3a"/><stop offset="100%" stop-color="#1a1a24"/>
            </linearGradient>
            <linearGradient id="screen-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
            </linearGradient>
            <filter id="sh-{uid}"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-opacity="0.45"/></filter>
            <linearGradient id="sheen-{uid}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="white" stop-opacity="0.07"/><stop offset="60%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path d="M 30 30 Q 10 30 10 55 L 10 110 Q 10 145 0 170 Q 0 195 20 195 L 320 195 Q 340 195 340 170 Q 330 145 330 110 L 330 55 Q 330 30 310 30 Z"
                fill="black" opacity="0.35" filter="url(#sh-{uid})" transform="translate(2,6)"/>
          <path d="M 30 30 Q 10 30 10 55 L 10 110 Q 10 145 0 170 Q 0 192 20 192 L 320 192 Q 340 192 340 170 Q 330 145 330 110 L 330 55 Q 330 30 310 30 Z"
                fill="url(#body-{uid})"/>
          <path d="M 30 30 Q 10 30 10 55 L 10 110 L 330 110 L 330 55 Q 330 30 310 30 Z"
                fill="url(#sheen-{uid})"/>
          <rect x="95" y="28" width="150" height="104" rx="6" fill="#0a0a12"/>
          <rect x="99" y="32" width="142" height="96" rx="4" fill="url(#screen-{uid})"/>
          <text x="170" y="74" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" font-weight="700" fill="white" opacity="0.8">{storage.label}</text>
          {#if storage.size_gb}
            <text x="170" y="95" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill={ac} opacity="0.9">{fmtSize(storage.size_gb)}</text>
          {/if}
          <rect x="99" y="32" width="142" height="30" rx="4" fill="white" opacity="0.03"/>
          <rect x="22" y="22" width="52" height="12" rx="6" fill="#3f3f52"/>
          <rect x="18" y="10" width="44" height="14" rx="7" fill="#35354a"/>
          <circle cx="68" cy="70" r="18" fill="#252536"/>
          <circle cx="68" cy="70" r="13" fill="#1e1e2e"/>
          <circle cx="68" cy="70" r="8" fill={ac} opacity="0.5"/>
          <rect x="44" y="112" width="14" height="42" rx="4" fill="#252536"/>
          <rect x="34" y="122" width="34" height="14" rx="4" fill="#252536"/>
          <rect x="50" y="126" width="10" height="10" rx="2" fill={ac} opacity="0.4"/>
          <rect x="266" y="22" width="52" height="12" rx="6" fill="#3f3f52"/>
          <rect x="278" y="10" width="44" height="14" rx="7" fill="#35354a"/>
          <circle cx="272" cy="128" r="18" fill="#252536"/>
          <circle cx="272" cy="128" r="13" fill="#1e1e2e"/>
          <circle cx="272" cy="128" r="8" fill={ac} opacity="0.5"/>
          <circle cx="286" cy="84" r="9" fill="#252536"/>
          <circle cx="272" cy="72" r="9" fill="#252536"/>
          <circle cx="258" cy="84" r="9" fill="#252536"/>
          <circle cx="272" cy="96" r="9" fill="#252536"/>
          <text x="286" y="88" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" font-weight="700" fill={ac} opacity="0.8">A</text>
          <text x="272" y="76" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" font-weight="700" fill={ac} opacity="0.8">X</text>
          <text x="258" y="88" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" font-weight="700" fill={ac} opacity="0.8">B</text>
          <text x="272" y="100" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" font-weight="700" fill={ac} opacity="0.8">Y</text>
          <circle cx="140" cy="142" r="8" fill="#252536"/>
          <circle cx="170" cy="148" r="10" fill={ac} opacity="0.85"/>
          <circle cx="200" cy="142" r="8" fill="#252536"/>
          <circle cx="170" cy="148" r="6" fill="rgba(0,0,0,0.3)"/>
          <circle cx="170" cy="148" r="3" fill="rgba(255,255,255,0.4)"/>
          <circle cx="116" cy="120" r="16" fill="#222232" opacity="0.8"/>
          <circle cx="224" cy="120" r="16" fill="#222232" opacity="0.8"/>
          <rect x="155" y="190" width="30" height="5" rx="2.5" fill="#3f3f52"/>
          <circle cx="148" cy="26" r="3" fill="#3f3f52"/>
          <circle cx="160" cy="26" r="3" fill="#3f3f52"/>
          <circle cx="180" cy="26" r="3" fill="#3f3f52"/>
          <circle cx="192" cy="26" r="3" fill="#3f3f52"/>
        </svg>
      </div>
    {/if}

    <!-- Info panel -->
    <div class="flex-1 min-w-0">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <div class="flex items-center gap-2.5 flex-wrap">
            <h1 class="text-2xl sm:text-3xl font-bold">{storage.label}</h1>
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold flex-shrink-0"
                  style="background:{storage.color}22; color:{storage.color}">
              {typeLabel(storage.type)}
            </span>
          </div>
          {#if storage.brand || storage.model}
            <p class="text-slate-500 dark:text-slate-400 mt-1">
              {[storage.brand, storage.model].filter(Boolean).join(" · ")}
            </p>
          {/if}
        </div>
        <div class="flex items-center gap-1">
        <button
          class="flex-shrink-0 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
          onclick={() => showEditStorage = true}
          title="Edit storage"
          aria-label="Edit storage">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </button>
        <button
          class="flex-shrink-0 text-red-400 hover:text-red-500 p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
          onclick={() => confirmDeleteStorage = true}
          disabled={deletingStorage}
          title="Delete storage"
          aria-label="Delete storage">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
        </div>
      </div>

      <!-- Stats chips -->
      <div class="flex flex-wrap gap-2 mt-4">
        {#if storage.size_gb}
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300">
            {fmtSize(storage.size_gb)}
          </span>
        {/if}
        {#if storage.free_gb != null}
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300">
            {fmtSize(storage.free_gb)} free
          </span>
        {/if}
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary-light">
          {games.length} {games.length === 1 ? "game" : "games"}
        </span>
      </div>

      <!-- Capacity bar -->
      {#if pct !== null}
        <div class="mt-5">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-1.5">
            <span>{pct}% used</span>
            <span>{fmtSize(storage.free_gb!)} free of {fmtSize(storage.size_gb!)}</span>
          </div>
          <div class="h-2 rounded-full bg-slate-200 dark:bg-white/10 overflow-hidden">
            <div class="h-full rounded-full transition-all" style="width:{pct}%; background:{storage.color}"></div>
          </div>
        </div>
      {/if}

      {#if storage.notes}
        <p class="mt-4 text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{storage.notes}</p>
      {/if}
    </div>
  </div>

  <!-- Games section -->
  <div class="flex items-center justify-between mb-5">
    <h2 class="font-bold text-lg">
      Games
      <span class="text-slate-400 dark:text-slate-500 font-normal text-base ml-1">({games.length})</span>
    </h2>
    <button class="btn-primary text-sm" onclick={() => showAddGame = true}>+ Add Game</button>
  </div>

  {#if games.length === 0}
    <div class="card p-10 text-center text-slate-400 dark:text-slate-500">
      <p class="text-4xl mb-3">🎮</p>
      <p class="font-medium">No games yet</p>
      <p class="text-sm mt-1">Add your first game to this storage medium</p>
    </div>
  {:else}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
      {#each games as game}
        <a href="/games/{game.id}"
           class="card group block overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-150">
          <div class="aspect-[3/4] bg-slate-100 dark:bg-white/5 relative">
            {#if game.cover_url}
              <img src={game.cover_url} alt={game.title} class="w-full h-full object-cover" loading="lazy" />
            {:else}
              <div class="w-full h-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-slate-300 dark:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
                </svg>
              </div>
            {/if}
            <button
              class="absolute top-1.5 right-1.5 w-7 h-7 rounded-lg bg-black/60 backdrop-blur-sm text-white
                     opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:bg-red-500"
              onclick={(e) => { e.preventDefault(); e.stopPropagation(); confirmGameId = game.id; }}
              disabled={deletingGame === game.id}
              aria-label="Remove game">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
            {#if game.rating}
              <span class="absolute bottom-1.5 left-1.5 bg-black/60 backdrop-blur-sm text-amber-400 text-xs font-bold px-1.5 py-0.5 rounded-md">
                ★ {Math.round(game.rating)}
              </span>
            {/if}
          </div>
          <div class="p-2.5">
            <p class="text-xs font-semibold leading-snug line-clamp-2">{game.title}</p>
            {#if game.release_year}
              <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{game.release_year}</p>
            {/if}
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>

{#if confirmGameId !== null}
  {@const gameTitle = games.find((g) => g.id === confirmGameId)?.title ?? "this game"}
  <ConfirmDialog
    title="Remove game"
    message={`Remove "${gameTitle}" from ${storage.label}?`}
    confirmLabel="Remove"
    onConfirm={() => { const id = confirmGameId!; confirmGameId = null; deleteGame(id); }}
    onCancel={() => confirmGameId = null}
  />
{/if}

{#if confirmDeleteStorage}
  <ConfirmDialog
    title="Delete storage"
    message={`Delete "${storage.label}" and all ${games.length} ${games.length === 1 ? 'game' : 'games'} on it? This cannot be undone.`}
    confirmLabel="Delete"
    onConfirm={() => { confirmDeleteStorage = false; deleteStorage(); }}
    onCancel={() => confirmDeleteStorage = false}
  />
{/if}

{#if showEditStorage}
  <EditStorageModal
    storage={storage}
    onClose={() => showEditStorage = false}
    showToast={(m, t) => toast.show(m, t)}
  />
{/if}

{#if showAddGame}
  <AddGameModal
    storageMediumId={storage.id}
    onClose={() => showAddGame = false}
    onAdded={onGameAdded}
    showToast={(m, t) => toast.show(m, t)}
  />
{/if}
