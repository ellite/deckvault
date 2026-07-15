<script lang="ts">
  interface StorageMedium {
    id: number; type: string; label: string; brand?: string; model?: string;
    size_gb?: number; free_gb?: number; notes?: string; color: string;
    color_primary?: string; color_secondary?: string;
  }
  interface Props {
    storage: StorageMedium;
    onClose: () => void;
    showToast: (msg: string, type?: "success" | "error") => void;
  }
  let { storage, onClose, showToast }: Props = $props();

  let label = $state(storage.label);
  let brand = $state(storage.brand ?? "");
  let model = $state(storage.model ?? "");
  let size_gb = $state(storage.size_gb?.toString() ?? "");
  let free_gb = $state(storage.free_gb?.toString() ?? "");
  let notes = $state(storage.notes ?? "");
  let color = $state(storage.color);
  let color_primary = $state(storage.color_primary ?? "#dc2626");
  let color_secondary = $state(storage.color_secondary ?? "#1c1c2e");
  let loading = $state(false);
  let error = $state("");

  const ACCENT_COLORS = ["#6366f1","#8b5cf6","#ec4899","#ef4444","#f59e0b","#10b981","#06b6d4","#3b82f6"];
  const PRIMARY_COLORS = ["#dc2626","#ea580c","#d97706","#16a34a","#2563eb","#7c3aed","#db2777","#e5e7eb"];
  const SECONDARY_COLORS = ["#1c1c2e","#111827","#1e293b","#0f172a","#18181b","#374151","#292524","#1a1a1a"];
  const PCB_COLORS = ["#15803d","#166534","#14532d","#1e3a5f","#1e1b4b","#1c1c2e","#111827","#18181b"];

  async function submit() {
    if (!label.trim()) { error = "Label is required"; return; }
    loading = true; error = "";
    try {
      const res = await fetch(`/api/storage/${storage.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
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
        throw new Error(d.detail ?? "Failed to update");
      }
      showToast("Storage updated!");
      onClose();
      window.location.reload();
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
      <h2 class="text-lg font-bold">Edit Storage</h2>
      <button class="btn-ghost p-1.5" onclick={onClose} aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Label -->
    <div>
      <label class="label" for="edit-label">Label *</label>
      <input id="edit-label" class="input" bind:value={label} placeholder="e.g. SanDisk Pro 512GB" />
    </div>

    <!-- Brand + Model (all types) -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="label" for="edit-brand">Brand</label>
        <input id="edit-brand" class="input" bind:value={brand} placeholder="SanDisk" />
      </div>
      <div>
        <label class="label" for="edit-model">Model</label>
        <input id="edit-model" class="input" bind:value={model} placeholder="Extreme Pro" />
      </div>
    </div>

    <!-- Size + Free -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="label" for="edit-size">Size (GB)</label>
        <input id="edit-size" type="number" class="input" bind:value={size_gb} placeholder="512" min="0" />
      </div>
      <div>
        <label class="label" for="edit-free">Free (GB)</label>
        <input id="edit-free" type="number" class="input" bind:value={free_gb} placeholder="256" min="0" />
      </div>
    </div>

    <!-- Notes -->
    <div>
      <label class="label" for="edit-notes">Notes</label>
      <textarea id="edit-notes" class="input resize-none h-20" bind:value={notes} placeholder="Optional notes…"></textarea>
    </div>

    <!-- SD card color preview + pickers -->
    {#if storage.type === "sdcard"}
      <div>
        <label class="label">Card Preview</label>
        <div class="rounded-xl overflow-hidden flex flex-col shadow-sm" style="height:72px">
          <div class="flex items-center justify-center text-white text-xs font-bold px-3 truncate flex-shrink-0"
               style="background:{color_primary}; height:40%">
            {brand || "Brand"} {model ? `· ${model}` : ""}
          </div>
          <div class="flex items-center justify-center text-white text-sm font-bold px-3 truncate"
               style="background:{color_secondary}; height:60%">
            {size_gb ? `${size_gb} GB` : "Capacity"}
          </div>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Top Color (Brand)</label>
          <div class="flex gap-1.5 flex-wrap">
            {#each PRIMARY_COLORS as c}
              <button type="button" onclick={() => color_primary = c}
                class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                       {color_primary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
                style="background:{c}" aria-label={c}></button>
            {/each}
            <input type="color" bind:value={color_primary} class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" />
          </div>
        </div>
        <div>
          <label class="label">Bottom Color (Body)</label>
          <div class="flex gap-1.5 flex-wrap">
            {#each SECONDARY_COLORS as c}
              <button type="button" onclick={() => color_secondary = c}
                class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                       {color_secondary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
                style="background:{c}" aria-label={c}></button>
            {/each}
            <input type="color" bind:value={color_secondary} class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" />
          </div>
        </div>
      </div>
    {/if}

    <!-- SSD PCB color -->
    {#if storage.type === "ssd"}
      <div>
        <label class="label">PCB Color</label>
        <div class="flex gap-1.5 flex-wrap items-center">
          {#each PCB_COLORS as c}
            <button type="button" onclick={() => color_primary = c}
              class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                     {color_primary === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
              style="background:{c}" aria-label={c}></button>
          {/each}
          <input type="color" bind:value={color_primary} class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" />
        </div>
      </div>
    {/if}

    <!-- Sidebar accent color -->
    <div>
      <label class="label">Accent Color</label>
      <div class="flex gap-2 flex-wrap">
        {#each ACCENT_COLORS as c}
          <button type="button" onclick={() => color = c}
            class="w-7 h-7 rounded-full ring-offset-2 ring-offset-white dark:ring-offset-surface-dark transition-all
                   {color === c ? 'ring-2 ring-slate-400 scale-110' : 'opacity-70 hover:opacity-100'}"
            style="background:{c}" aria-label={c}></button>
        {/each}
        <input type="color" bind:value={color} class="w-7 h-7 rounded-full cursor-pointer border-0 bg-transparent p-0" />
      </div>
    </div>

    {#if error}
      <p class="text-sm text-red-500">{error}</p>
    {/if}

    <div class="flex gap-3 pt-1">
      <button class="btn-ghost flex-1" onclick={onClose}>Cancel</button>
      <button class="btn-primary flex-1" onclick={submit} disabled={loading}>
        {loading ? "Saving…" : "Save Changes"}
      </button>
    </div>
  </div>
</div>
