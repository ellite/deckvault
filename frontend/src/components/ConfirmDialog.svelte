<script lang="ts">
  interface Props {
    title: string;
    message: string;
    confirmLabel?: string;
    onConfirm: () => void;
    onCancel: () => void;
  }
  let { title, message, confirmLabel = "Delete", onConfirm, onCancel }: Props = $props();

  function onKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") onCancel();
  }
</script>

<svelte:window onkeydown={onKeydown} />

<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onclick={onCancel}></div>
  <div class="relative w-full max-w-sm card p-6 shadow-2xl">
    <h2 class="text-lg font-bold mb-2">{title}</h2>
    <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">{message}</p>
    <div class="flex gap-3 justify-end">
      <button class="btn-ghost text-sm" onclick={onCancel}>Cancel</button>
      <button class="btn-danger text-sm" onclick={onConfirm}>{confirmLabel}</button>
    </div>
  </div>
</div>
