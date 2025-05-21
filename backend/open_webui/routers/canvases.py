from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request

from open_webui.models.canvas import (
    CanvasModel,
    CanvasForm,
    Canvases,
    CanvasProcessRequest,
    CanvasProcessResponse,
)
from open_webui.utils.auth import get_verified_user
from open_webui.models.users import UserModel
from open_webui.utils.ai_processing import process_canvas_content_with_ai
from open_webui.constants import ERROR_MESSAGES

router = APIRouter()

@router.post("/new", response_model=Optional[CanvasModel])
async def create_new_canvas(
    form_data: CanvasForm, user: UserModel = Depends(get_verified_user)
):
    canvas = Canvases.insert_new_canvas(user.id, form_data)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT,
        )
    return canvas

@router.get("/{canvas_id}", response_model=Optional[CanvasModel])
async def get_canvas(
    canvas_id: str, user: UserModel = Depends(get_verified_user)
):
    canvas = Canvases.get_canvas_by_id(canvas_id, user.id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    return canvas

@router.get("/", response_model=List[CanvasModel])
async def get_all_canvases(user: UserModel = Depends(get_verified_user)):
    return Canvases.get_canvases_by_user_id(user.id)

@router.post("/{canvas_id}", response_model=Optional[CanvasModel])
async def update_canvas(
    canvas_id: str,
    form_data: CanvasForm,
    user: UserModel = Depends(get_verified_user),
):
    canvas = Canvases.update_canvas_by_id(canvas_id, user.id, form_data)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    return canvas

@router.delete("/{canvas_id}", response_model=bool)
async def delete_canvas(
    canvas_id: str, user: UserModel = Depends(get_verified_user)
):
    success = Canvases.delete_canvas_by_id(canvas_id, user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    return success


@router.post("/{canvas_id}/process_content", response_model=CanvasProcessResponse)
async def process_canvas_content_endpoint(
    request_obj: Request,
    canvas_id: str,
    payload: CanvasProcessRequest,
    user: UserModel = Depends(get_verified_user),
):
    # Verify canvas exists and user has access
    canvas = Canvases.get_canvas_by_id(canvas_id, user.id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    # Use payload.content as the primary source.
    # Could add logic here: if not payload.content and canvas.data: use canvas.data
    content_to_process = payload.content
    if not content_to_process and canvas.data: # Example fallback
        content_to_process = canvas.data


    if not content_to_process:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No content provided for processing."
        )

    ai_response_content = await process_canvas_content_with_ai(
        request=request_obj,
        user=user,
        content=content_to_process,
        command=payload.command,
        target_model_id=payload.model_id,
    )

    if ai_response_content is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing content with AI.",
        )

    return CanvasProcessResponse(processed_content=ai_response_content)
