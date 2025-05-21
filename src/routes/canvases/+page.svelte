<script lang="ts">
  import { onMount } from 'svelte';
  import { getCanvases, deleteCanvasById, type Canvas } from '$lib/apis/canvases';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { PlusCircleIcon, TrashIcon, EditIcon } from 'svelte-feather-icons';

  let canvases: Canvas[] = [];
  let isLoading: boolean = true;
  let errorLoading: string | null = null;

  onMount(async () => {
    fetchCanvases();
  });

  const fetchCanvases = async () => {
    isLoading = true;
    errorLoading = null;
    try {
      canvases = await getCanvases();
    } catch (error) {
      console.error('Error fetching canvases:', error);
      toast.error(`Error fetching canvases: ${error.message}`);
      errorLoading = error.message;
    } finally {
      isLoading = false;
    }
  };

  const handleCreateNewCanvas = () => {
    goto('/canvas/new');
  };

  const handleDeleteCanvas = async (canvasId: string, canvasTitle: string) => {
    if (!confirm(`Are you sure you want to delete the canvas "${canvasTitle}"?`)) {
      return;
    }
    toast.info(`Deleting canvas "${canvasTitle}"...`);
    try {
      await deleteCanvasById(canvasId);
      canvases = canvases.filter((canvas) => canvas.id !== canvasId);
      toast.success(`Canvas "${canvasTitle}" deleted successfully.`);
    } catch (error) {
      console.error('Error deleting canvas:', error);
      toast.error(`Error deleting canvas: ${error.message}`);
    }
  };

  const formatDate = (timestamp: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };
</script>

<style>
  .canvases-page {
    padding: 1rem;
    max-width: 1000px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .page-header h1 {
    font-size: 1.8rem;
    color: #333;
  }

  .create-new-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }

  .create-new-btn:hover {
    background-color: #0056b3;
  }

  .loading-indicator,
  .error-message {
    text-align: center;
    font-size: 1.2rem;
    color: #555;
    margin-top: 2rem;
  }
  
  .empty-state {
    text-align: center;
    font-size: 1.1rem;
    color: #777;
    margin-top: 2rem;
  }

  .canvases-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .canvas-card {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .canvas-card:hover {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }

  .canvas-card h3 {
    font-size: 1.1rem;
    margin-top: 0;
    margin-bottom: 0.5rem;
    color: #333;
    word-break: break-all; /* To prevent long titles from breaking layout */
  }

  .canvas-card p {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.3rem;
  }
  
  .canvas-card .chat-id {
    font-size: 0.8rem;
    color: #888;
    margin-bottom: 0.8rem;
    font-style: italic;
  }

  .card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .card-actions button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.3rem;
    color: #555;
    transition: color 0.2s;
  }
  
  .card-actions button.edit-btn:hover {
    color: #007bff;
  }
  
  .card-actions button.delete-btn:hover {
    color: #dc3545;
  }

</style>

<div class="canvases-page">
  <div class="page-header">
    <h1>My Canvases</h1>
    <button class="create-new-btn" on:click={handleCreateNewCanvas}>
      <PlusCircleIcon size="20" />
      Create New Canvas
    </button>
  </div>

  {#if isLoading}
    <div class="loading-indicator">
      <p>Loading canvases...</p>
    </div>
  {:else if errorLoading}
    <div class="error-message">
      <p>Error loading canvases: {errorLoading}. Please try again later.</p>
      <button on:click={fetchCanvases}>Retry</button>
    </div>
  {:else if canvases.length === 0}
    <div class="empty-state">
      <p>You don't have any canvases yet. Get started by creating one!</p>
    </div>
  {:else}
    <div class="canvases-grid">
      {#each canvases as canvas (canvas.id)}
        <div class="canvas-card">
          <div>
            <h3>{canvas.title}</h3>
            <p>Last Updated: {formatDate(canvas.updated_at)}</p>
            <p>Created: {formatDate(canvas.created_at)}</p>
            {#if canvas.chat_id}
              <p class="chat-id" title="Associated Chat ID">Chat: {canvas.chat_id.substring(0,8)}...</p>
            {/if}
          </div>
          <div class="card-actions">
            <button
              class="edit-btn"
              title="Edit Canvas"
              on:click={() => goto(`/canvas/${canvas.id}`)}
            >
              <EditIcon size="18" />
            </button>
            <button
              class="delete-btn"
              title="Delete Canvas"
              on:click={() => handleDeleteCanvas(canvas.id, canvas.title)}
            >
              <TrashIcon size="18" />
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
