<script lang="ts">
  import CanvasEditor from '$lib/components/canvas/CanvasEditor.svelte';
  import { page } from '$app/stores';

  let canvasId: string;

  $: canvasId = $page.params.id;
</script>

{#if canvasId}
  <CanvasEditor {canvasId} />
{:else}
  <p>Loading canvas information...</p>
{/if}
