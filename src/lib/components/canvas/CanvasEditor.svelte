<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  // import { Editor } from '@tiptap/core'; // Commented out: TipTap
  // import StarterKit from '@tiptap/starter-kit'; // Commented out: TipTap
  // import { Tiptap } from 'svelte-tiptap'; // Commented out: TipTap
  import { getCanvasById, updateCanvasById, createCanvas, processCanvasContent, type Canvas } from '$lib/apis/canvases'; // Added processCanvasContent
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { user, models } from '$lib/stores'; // Assuming user store exists, added models for potential model_id selection
  import { toast } from 'svelte-sonner';

  export let canvasId: string = '';

  let currentCanvas: Canvas | null = null;
  let canvasTitle: string = 'Untitled Canvas';
  // let editor: Editor | null = null; // Commented out: TipTap
  let isLoading: boolean = true;
  let isSaving: boolean = false;
  let textContent: string = ""; // For textarea, replacing Tiptap

  // AI Processing State
  let selectedCommand: string = "summarize";
  let aiCommands: string[] = ["summarize", "explain_code", "echo"]; // Added "echo" for testing
  let isProcessingAI: boolean = false;
  let aiResponse: string = ""; // To temporarily store or display AI response

  let editorContentElement: HTMLElement; // For direct DOM manipulation if not using Tiptap component, might not be needed with textarea

  onMount(async () => {
    const loadOrCreateCanvas = async () => {
      if (canvasId === 'new' || !canvasId) {
        try {
          toast.info('Creating new canvas...');
          const newCanvas = await createCanvas({ title: 'Untitled Canvas', data: {} });
          currentCanvas = newCanvas;
          canvasTitle = newCanvas.title;
          // Initialize editor with empty content
          // if (editorContentElement) { // Commented out: TipTap
          //   editor = new Editor({
          //     element: editorContentElement,
          //     extensions: [StarterKit],
          //     content: {},
          //     editable: true,
          //   });
          // }
          isLoading = false;
          toast.success('New canvas created');
          goto(`/canvas/${newCanvas.id}`, { replaceState: true });
        } catch (error) {
          console.error('Error creating canvas:', error);
          toast.error(`Error creating canvas: ${error.message}`);
          goto('/'); // Navigate to a safe page
        }
      } else {
        try {
          isLoading = true;
          toast.info(`Loading canvas ${canvasId}...`);
          const fetchedCanvas = await getCanvasById(canvasId);
          currentCanvas = fetchedCanvas;
          canvasTitle = fetchedCanvas.title;
          // Initialize editor with fetched content
          // if (editorContentElement) { // Commented out: TipTap
          //   editor = new Editor({
          //     element: editorContentElement,
          //     extensions: [StarterKit],
          //     content: fetchedCanvas.data || {},
          //     editable: true,
          //   });
          // }
          
          // Initialize textContent based on fetchedCanvas.data
          if (typeof fetchedCanvas.data === 'string') {
            textContent = fetchedCanvas.data;
          } else if (fetchedCanvas.data && typeof fetchedCanvas.data === 'object') {
            // If it's an object (like from previous TipTap JSON), stringify it for the textarea
            // Or extract relevant text part if structure is known. For now, stringify.
            const placeholderData = fetchedCanvas.data as any;
            if (placeholderData?.placeholder && typeof placeholderData.placeholder === 'string') {
              textContent = placeholderData.placeholder; // From previous placeholder
            } else {
              textContent = JSON.stringify(fetchedCanvas.data, null, 2);
            }
          } else {
            textContent = ""; // Default to empty if data is null/undefined or not string/object
          }

          isLoading = false;
          toast.success(`Canvas "${fetchedCanvas.title}" loaded`);
        } catch (error) {
          console.error('Error fetching canvas:', error);
          toast.error(`Error fetching canvas: ${error.message}`);
          if (error.message.includes('Not Found') || error.message.includes('404')) {
            goto('/canvases'); // Or some other relevant page
          } else {
            goto('/');
          }
        }
      }
    };
    loadOrCreateCanvas();
  });

  const saveCanvas = async () => {
    if (!currentCanvas /*|| !editor*/) { // Commented out: TipTap editor check
      toast.error('Canvas or editor not available for saving.');
      return;
    }
    isSaving = true;
    toast.info('Saving canvas...');
    try {
      // Determine data to save based on textContent
      let dataToSave: any = textContent;
      // If canvas.data was intended to be JSON, try to parse it.
      // For now, let's assume it's saved as a string if TipTap is not used.
      // If you expect JSON:
      // try {
      //   dataToSave = JSON.parse(textContent);
      // } catch (e) {
      //   // If parsing fails, save as plain text or wrap in a structure
      //   console.warn("Content is not valid JSON, saving as text string or wrapped object.");
      //   dataToSave = { text_content: textContent }; // Example: wrap plain text
      // }
      // For the current setup with textarea, saving raw textContent is simplest.
      // If TipTap was outputting JSON, this would be editor.getJSON().
      // Since we use a textarea, currentCanvas.data will store the string from textContent.

      currentCanvas.data = dataToSave; // Update currentCanvas's data before saving

      const updatedCanvas = await updateCanvasById(currentCanvas.id, {
        title: canvasTitle,
        data: dataToSave, // Save the content from textContent
      });
      currentCanvas.updated_at = updatedCanvas.updated_at;
      currentCanvas.title = updatedCanvas.title;
      canvasTitle = updatedCanvas.title; // Ensure local title is also updated

      toast.success('Canvas saved successfully!');
    } catch (error) {
      console.error('Error saving canvas:', error);
      toast.error(`Error saving canvas: ${error.message}`);
    } finally {
      isSaving = false;
    }
  };

  onDestroy(() => {
    // if (editor) { // Commented out: TipTap
    //   editor.destroy();
    // }
  });

  async function processWithAI() {
    if (!currentCanvas) {
      toast.error('Canvas not loaded.');
      return;
    }
    isProcessingAI = true;
    aiResponse = ""; // Clear previous response

    // Use textContent as the content to process
    let contentToProcess: string | object = textContent;
    
    // If currentCanvas.data was meant to hold structured JSON from Tiptap,
    // and textContent is a string representation of that:
    // try { contentToProcess = JSON.parse(textContent); } 
    // catch (e) { /* it's a string, use as is, or handle error */ }
    // For now, we assume textContent is the raw string to be processed.

    try {
      // Optional: Select a model if your UI allows it, otherwise backend picks default
      // const selectedModelId = $models.length > 0 ? $models[0].id : undefined; 

      const result = await processCanvasContent(
        currentCanvas.id,
        contentToProcess,
        selectedCommand
        // model_id: selectedModelId // Optional: Pass a specific model_id
      );
      
      // Update textContent with the processed content
      textContent = result.processed_content;
      
      // Update currentCanvas.data (assuming textContent is the source of truth for the view)
      currentCanvas.data = textContent; // Store as string, matching textarea
      
      // Example: if canvas.data should store JSON (and result.processed_content is JSON string):
      // try { 
      //   currentCanvas.data = JSON.parse(result.processed_content); 
      // } catch (e) { 
      //   currentCanvas.data = { text_content: result.processed_content }; // Fallback
      //   toast.warning("AI response was not valid JSON, stored as text.");
      // }

      aiResponse = `AI Response for '${selectedCommand}':\n${result.processed_content}`; // For display if needed
      toast.success(`Content processed with AI using command: ${selectedCommand}`);

      // Automatically save the canvas with the new AI-processed content
      await saveCanvas(); 
    } catch (error) {
      console.error("Error processing with AI:", error);
      toast.error(`AI Processing Error: ${error.message}`);
      aiResponse = `Error: ${error.message}`;
    } finally {
      isProcessingAI = false;
    }
  }

  const formatDate = (timestamp: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };
</script>

<style>
  .ai-tools-section {
    display: flex;
    align-items: center;
    gap: 0.5rem; /* Reduced gap */
    margin-bottom: 1rem; /* Add some space below AI tools */
  }

  .ai-tools-section select,
  .ai-tools-section button {
    padding: 0.4rem 0.8rem; /* Slightly smaller padding */
    font-size: 0.9rem; /* Slightly smaller font */
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .ai-tools-section button {
    background-color: #28a745; /* Green for AI action */
    color: white;
    cursor: pointer;
  }

  .ai-tools-section button:disabled {
    background-color: #ccc;
  }

  .canvas-editor-layout {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 100px); /* Adjust as needed based on header/nav height */
    padding: 1rem;
    gap: 1rem;
  }

  .editor-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #ccc;
  }

  .editor-header input[type="text"] {
    flex-grow: 1;
    font-size: 1.2rem;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .editor-header button {
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .editor-header button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .timestamps {
    font-size: 0.8rem;
    color: #666;
  }
  
  .timestamps p {
    margin: 0;
  }

  .tiptap-editor-container { /* Renamed to content-area or similar might be better if TipTap is gone */
    border: 1px solid #ccc;
    min-height: 400px; /* Ensure it's visible */
    flex-grow: 1;
    padding: 0; /* Remove padding if textarea has its own */
    overflow-y: auto;
    background-color: #f9f9f9;
    display: flex; /* To make textarea fill */
  }

  .content-area textarea {
    width: 100%;
    height: 100%; /* Make textarea fill the container */
    padding: 1rem;
    border: none; /* Remove default textarea border if container has one */
    border-radius: 0; /* Remove radius if container has one */
    resize: vertical; /* Allow vertical resize */
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
  }


  .loading-indicator, .ai-processing-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 1.5rem;
  }
</style>

{#if isLoading}
  <div class="loading-indicator">
    <p>Loading Canvas...</p>
  </div>
{:else}
  <div class="canvas-editor-layout">
    <div class="editor-header">
      <input type="text" bind:value={canvasTitle} placeholder="Canvas Title" disabled={isLoading || isSaving || isProcessingAI} />
      <button on:click={saveCanvas} disabled={isSaving || isLoading || isProcessingAI}>
        {#if isSaving}Saving...{:else}Save Canvas{/if}
      </button>
      {#if currentCanvas}
        <div class="canvas-meta">
          <div class="timestamps">
            <p>Created: {formatDate(currentCanvas.created_at)}</p>
            <p>Updated: {formatDate(currentCanvas.updated_at)}</p>
          </div>
          {#if currentCanvas.chat_id}
            <div class="linked-chat">
              <p>
                Linked to Chat:
                <a href="/c/{currentCanvas.chat_id}" title="Go to associated chat">
                  {currentCanvas.chat_id.substring(0, 8)}...
                </a>
              </p>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="ai-tools-section">
      <select bind:value={selectedCommand} disabled={isProcessingAI || isLoading || isSaving}>
        {#each aiCommands as cmd}
          <option value={cmd}>{cmd.replace(/_/g, " ").toUpperCase()}</option>
        {/each}
      </select>
      <button on:click={processWithAI} disabled={isProcessingAI || isLoading || isSaving}>
        {#if isProcessingAI}
          Processing with AI...
        {:else}
          Process with AI
        {/if}
      </button>
    </div>
    
    {#if isProcessingAI}
      <div class="ai-processing-indicator">
        <p>AI is thinking... ✨</p>
      </div>
    {/if}

    <div class="content-area" style="flex-grow: 1; display: flex;">
      <textarea 
        bind:value={textContent} 
        class="w-full h-full p-2 border rounded" 
        placeholder="Canvas content area..."
        disabled={isLoading || isSaving || isProcessingAI}
        style="flex-grow: 1; min-height: 300px;"
      ></textarea>
    </div>

    {#if aiResponse && !isProcessingAI} <!-- Show AI response only after processing and if not currently processing -->
        <div class="mt-4 p-2 border bg-gray-100 dark:bg-gray-800 rounded">
            <h3 class="font-semibold text-gray-700 dark:text-gray-300">Last AI Output ({selectedCommand}):</h3>
            <pre class="whitespace-pre-wrap text-sm text-gray-600 dark:text-gray-400">{aiResponse.replace(`AI Response for '${selectedCommand}':\n`, '')}</pre>
        </div>
    {/if}
  </div>
{/if}
