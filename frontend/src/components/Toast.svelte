<script lang="ts">
  import { onDestroy } from "svelte";

  let toasts: { id: number; message: string; type: "success" | "error" }[] = $state([]);
  let next = 0;

  export function show(message: string, type: "success" | "error" = "success") {
    const id = next++;
    toasts = [...toasts, { id, message, type }];
    setTimeout(() => remove(id), 3500);
  }

  function remove(id: number) {
    toasts = toasts.filter((t) => t.id !== id);
  }
</script>

<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
  {#each toasts as t (t.id)}
    <div
      class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium
             {t.type === 'success'
               ? 'bg-emerald-500 text-white'
               : 'bg-red-500 text-white'}"
    >
      {#if t.type === "success"}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      {/if}
      {t.message}
    </div>
  {/each}
</div>
