<script lang="ts">
  interface Props {
    onClose: () => void;
    onCreated: (medium: any) => void;
    showToast: (msg: string, type?: "success" | "error") => void;
  }
  let { onClose, onCreated, showToast }: Props = $props();

  let type = $state("sdcard");
  let label = $state("");
  let brand = $state("");
  let model = $state("");
  let size_gb = $state("");
  let free_gb = $state("");
  let notes = $state("");
  let color = $state("#6366f1");
  let color_primary = $state("#dc2626");
  let color_secondary = $state("#1c1c2e");
  let loading = $state(false);
  let error = $state("");

  const ACCENT_COLORS = ["#6366f1","#8b5cf6","#ec4899","#ef4444","#f59e0b","#10b981","#06b6d4","#3b82f6"];
  const PRIMARY_COLORS = ["#dc2626","#ea580c","#d97706","#16a34a","#2563eb","#7c3aed","#db2777","#e5e7eb"];
  const SECONDARY_COLORS = ["#1c1c2e","#111827","#1e293b","#0f172a","#18181b","#374151","#292524","#1a1a1a"];

  async function submit() {
    if (!label.trim()) { error = "Label is required"; return; }
    loading = true; error = "";
    try {
      const res = await fetch("/api/storage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type,
          label: label.trim(),
          brand: brand.trim() || null,
          model: model.trim() || null,
          size_gb: size_gb ? parseFloat(size_gb) : null,
          free_gb: free_gb ? parseFloat(free_gb) : null,
          notes: notes.trim() || null,
          color,
          color_primary,
          color_secondary,
        }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail ?? "Failed to create");
      }
      const created = await res.json();
      showToast("Storage added!");
      onCreated(created);
      onClose();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
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
  <div class="card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-5">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold">Add Storage Medium</h2>
      <button class="btn-ghost p-1.5" onclick={onClose} aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Type -->
    <div>
      <label class="label">Type</label>
      <div class="grid grid-cols-2 gap-2">
        {#each [["local","🎮 Internal"],["sdcard","💾 SD Card"],["hdd","🖴 HDD"],["ssd","⚡ SSD (M.2)"]] as [val, lbl]}
          <button
            type="button"
            onclick={() => type = val}
            class="py-3 rounded-xl border-2 text-sm font-semibold transition-colors
                   {type === val
                     ? 'border-primary bg-primary/10 text-primary dark:border-primary-light dark:text-primary-light'
                     : 'border-border dark:border-border-dark text-slate-500'}"
          >
            {lbl}
          </button>
        {/each}
      </div>
    </div>

    <!-- Label -->
    <div>
      <label class="label" for="storage-label">Label *</label>
      <input id="storage-label" class="input" bind:value={label} placeholder="e.g. SanDisk Pro 512GB" />
    </div>

    {#if type === "sdcard"}
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label" for="storage-brand">Brand</label>
          <input id="storage-brand" class="input" bind:value={brand} placeholder="SanDisk" />
        </div>
        <div>
          <label class="label" for="storage-model">Model</label>
          <input id="storage-model" class="input" bind:value={model} placeholder="Extreme Pro" />
        </div>
      </div>
    {/if}

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="label" for="storage-size">Size (GB)</label>
        <input id="storage-size" type="number" class="input" bind:value={size_gb} placeholder="512" min="0" />
      </div>
      <div>
        <label class="label" for="storage-free">Free (GB)</label>
        <input id="storage-free" type="number" class="input" bind:value={free_gb} placeholder="256" min="0" />
      </div>
    </div>

    <div>
      <label class="label" for="storage-notes">Notes</label>
      <textarea id="storage-notes" class="input resize-none h-20" bind:value={notes} placeholder="Optional notes…"></textarea>
    </div>

    <!-- SSD PCB color -->
    {#if type === "ssd"}
      <div>
        <label class="label">PCB Color</label>
        <div class="flex gap-1.5 flex-wrap items-center">
          {#each ["#15803d","#166534","#14532d","#1e3a5f","#1e1b4b","#1c1c2e","#111827","#18181b"] as c}
            <button type="button" onclick={() => color_primary = c}
              class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                     {color_primary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
              style="background:{c}" aria-label={c}></button>
          {/each}
          <input type="color" bind:value={color_primary}
            class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" title="Custom PCB color"/>
        </div>
      </div>
    {/if}

    <!-- Card color preview -->
    {#if type === "sdcard"}
      <div>
        <label class="label">Card Colors Preview</label>
        <div class="rounded-xl overflow-hidden flex flex-col" style="height:72px; box-shadow:0 2px 8px rgba(0,0,0,0.2)">
          <div class="flex items-center justify-center text-white text-xs font-bold px-3 truncate flex-shrink-0"
               style="background:{color_primary}; height:40%">
            {brand || "Brand"} {model ? `· ${model}` : ""}
          </div>
          <div class="flex items-center justify-center text-white text-sm font-bold px-3 truncate"
               style="background:{color_secondary}; height:60%">
            {size_gb ? `${size_gb}GB` : "Capacity"}
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Card Top Color (Brand)</label>
          <div class="flex gap-1.5 flex-wrap">
            {#each PRIMARY_COLORS as c}
              <button type="button" onclick={() => color_primary = c}
                class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                       {color_primary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
                style="background:{c}" aria-label={c}></button>
            {/each}
            <input type="color" bind:value={color_primary}
              class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" title="Custom color" />
          </div>
        </div>
        <div>
          <label class="label">Card Bottom Color (Body)</label>
          <div class="flex gap-1.5 flex-wrap">
            {#each SECONDARY_COLORS as c}
              <button type="button" onclick={() => color_secondary = c}
                class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                       {color_secondary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
                style="background:{c}" aria-label={c}></button>
            {/each}
            <input type="color" bind:value={color_secondary}
              class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" title="Custom color" />
          </div>
        </div>
      </div>
    {/if}

    <!-- Sidebar accent color -->
    <div>
      <label class="label">Sidebar Accent Color</label>
      <div class="flex gap-2 flex-wrap">
        {#each ACCENT_COLORS as c}
          <button
            type="button"
            onclick={() => color = c}
            class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                   {color === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
            style="background:{c}"
            aria-label={c}
          ></button>
        {/each}
      </div>
    </div>

    {#if error}
      <p class="text-sm text-red-500">{error}</p>
    {/if}

    <div class="flex gap-3 pt-1">
      <button class="btn-ghost flex-1" onclick={onClose}>Cancel</button>
      <button class="btn-primary flex-1" onclick={submit} disabled={loading}>
        {loading ? "Adding…" : "Add Storage"}
      </button>
    </div>
  </div>
</div>
