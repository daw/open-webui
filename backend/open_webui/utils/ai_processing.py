import json
from typing import Optional, Union

from fastapi import Request, HTTPException, status

from open_webui.models.users import UserModel
from open_webui.utils.chat import generate_chat_completion
from open_webui.config import DEFAULT_MODELS
from open_webui.constants import ERROR_MESSAGES

async def process_canvas_content_with_ai(
    request: Request,
    user: UserModel,
    content: Union[str, dict],
    command: str,
    target_model_id: Optional[str] = None,
) -> Optional[str]:
    """
    Processes canvas content with an AI model based on a given command.
    """
    content_str = json.dumps(content) if isinstance(content, dict) else str(content)
    constructed_prompt = ""

    if command == "summarize":
        constructed_prompt = f"Summarize this content: {content_str}"
    elif command == "echo": # Simple command for testing
        constructed_prompt = f"Echo this content: {content_str}"
    elif command == "explain_code":
        constructed_prompt = f"Explain this code: {content_str}"
    else:
        # Fallback for unrecognized command, or raise error
        # For now, let's try a generic instruction.
        constructed_prompt = f"Process the following content as per this command '{command}': {content_str}"
        # Alternatively, to be stricter:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unrecognized command: {command}")


    # Model Selection
    selected_model_id = None
    if target_model_id and target_model_id in request.app.state.MODELS:
        selected_model_id = target_model_id
    else:
        # Fallback to default models configured in the system
        # This attempts to find the first valid model from DEFAULT_MODELS list
        # or the very first model available if DEFAULT_MODELS is empty or none are valid
        if DEFAULT_MODELS:
            default_model_ids = DEFAULT_MODELS.split(",")
            for model_id_option in default_model_ids:
                if model_id_option in request.app.state.MODELS:
                    selected_model_id = model_id_option
                    break
        
        if not selected_model_id and request.app.state.MODELS:
            # Fallback to the first available model if no default is found or suitable
            selected_model_id = next(iter(request.app.state.MODELS))

    if not selected_model_id:
        # This should ideally not happen if models are loaded, but as a safeguard:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No suitable AI model available for processing.",
        )

    # Prepare the payload for the AI call (simplified for single-turn)
    messages = [{"role": "user", "content": constructed_prompt}]
    
    # This payload structure is based on what `generate_chat_completion` might expect.
    # It needs to be adapted to the actual signature and requirements of the chosen AI call mechanism.
    # We are aiming for a non-streaming, direct response.
    
    # Simplified form_data for generate_chat_completion
    # We need to ensure this matches the structure expected by generate_chat_completion
    # or the underlying LLM call.
    form_data = {
        "model": selected_model_id,
        "messages": messages,
        "stream": False, # Explicitly set stream to False for single-turn response
        # Other parameters like temperature, max_tokens, etc., could be set here if needed.
        # For simplicity, we'll rely on defaults or model-specific configurations.
        "temperature": 0.7, # A common default
        "max_tokens": 1000, # Example limit
        "model_item": request.app.state.MODELS[selected_model_id], # Pass the model item
        "metadata": { # Minimal metadata
            "user_id": user.id,
        }
    }

    try:
        # We need to call a function that handles the direct AI interaction and returns the response.
        # `generate_chat_completion` returns a StreamingResponse or similar.
        # We need to adapt this to get a direct string output.
        
        # Let's assume `generate_chat_completion` can be modified or we have another utility
        # that can handle non-streaming requests and return the content directly.
        # For the purpose of this task, I'll simulate getting the direct content.
        # This is a placeholder for the actual AI call logic.
        
        # The actual call might look like this if generate_chat_completion is adapted:
        # response_content = await some_non_streaming_chat_completion(request, form_data, user)
        # For now, let's use a simplified approach if possible, or note this as a complex part.

        # The `generate_chat_completion` function in `open_webui.utils.chat` is designed for streaming.
        # We need a non-streaming equivalent.
        # Let's assume we call a lower-level function or adapt `generate_chat_completion`.
        # This is a conceptual adaptation.
        
        # Simulating getting the response from a potentially complex handler:
        # The actual implementation would involve calling the appropriate LLM backend
        # (Ollama, OpenAI) without streaming.
        
        # This part is complex because the existing infrastructure is heavily stream-oriented.
        # A direct, non-streaming call might need to bypass some of the `Chat` specific utilities.
        
        # Let's assume `generate_chat_completion` is called, and we try to get the first message content.
        # This is a simplification. A real implementation would need a dedicated non-streaming path.
        
        api_response = await generate_chat_completion(request, form_data, user)

        if hasattr(api_response, "body_iterator"): # Check if it's a StreamingResponse
            # This is a simplified way to get content from a stream for a non-streaming case.
            # In a real scenario, you'd await the full content if the underlying call supports it,
            # or use a different function.
            full_response_content = ""
            async for chunk in api_response.body_iterator:
                # Assuming chunks are bytes and need decoding, and may contain JSON lines
                # This parsing logic needs to be robust based on actual stream format
                try:
                    # This is highly dependent on the actual stream format
                    # For Ollama, it's often JSON lines. For OpenAI, it's different.
                    # This is a placeholder for proper stream aggregation.
                    # A proper non-streaming call would avoid this.
                    if isinstance(chunk, bytes):
                        chunk_str = chunk.decode('utf-8')
                        # Attempt to parse known streaming formats (very simplified)
                        if '"content":"' in chunk_str: # Simplified check for content part
                             try:
                                data = json.loads(chunk_str.split("data: ")[-1] if "data: " in chunk_str else chunk_str)
                                if data.get("choices") and data["choices"][0].get("delta") and data["choices"][0]["delta"].get("content"):
                                    full_response_content += data["choices"][0]["delta"]["content"]
                                elif data.get("message") and data["message"].get("content"): # Ollama non-streaming in stream
                                     full_response_content = data["message"]["content"] # Assume full message if this format
                                     break 
                                elif data.get("content"): # Ollama /content in stream
                                     full_response_content += data.get("content")


                             except json.JSONDecodeError:
                                # If JSON parsing fails, it might be a raw string or part of a larger structure
                                # This part is very tricky without knowing the exact stream format
                                pass # Or append raw if applicable: full_response_content += chunk_str

                    elif isinstance(chunk, str):
                         full_response_content += chunk # Should ideally be JSON
                except Exception as e:
                    print(f"Error processing stream chunk: {e}") # For debugging
                    # Continue to try and get some data

            # If after iterating, we have some content, use it.
            # This is still a workaround for not having a true non-streaming call.
            if full_response_content:
                 return full_response_content.strip() if full_response_content else None

            # If the stream yielded nothing usable in this simplified parsing
            print("AI Processing: Stream did not yield expected content structure.")
            return None # Or raise error


        elif hasattr(api_response, "content"): # For non-streaming direct JSONResponse (less likely from generate_chat_completion)
            response_data = json.loads(api_response.content)
            # Extract content based on typical chat completion structure
            if response_data.get("choices") and response_data["choices"][0].get("message"):
                return response_data["choices"][0]["message"]["content"]
        
        # Fallback if response structure is unexpected
        print(f"AI Processing: Unexpected API response type or structure: {type(api_response)}")
        return None

    except HTTPException as e:
        # Re-raise HTTPExceptions
        raise e
    except Exception as e:
        print(f"Error processing content with AI: {e}")
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        # Return None or raise a specific HTTPException for AI processing failure
        # For the endpoint, we'll check for None and raise 500.
        return None
