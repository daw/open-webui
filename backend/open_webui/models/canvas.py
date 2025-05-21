import uuid
import time
from typing import Optional, List

from sqlalchemy import Column, String, Text, JSON, BigInteger
from pydantic import BaseModel, ConfigDict

from open_webui.models.database import Base, get_db

class Canvas(Base):
    __tablename__ = "canvas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    chat_id = Column(String, nullable=True)
    title = Column(Text, nullable=False, default="Untitled Canvas")
    data = Column(JSON, nullable=True, default=lambda: {})
    created_at = Column(BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = Column(
        BigInteger,
        nullable=False,
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time()),
    )

class CanvasModel(BaseModel):
    id: str
    user_id: str
    chat_id: Optional[str] = None
    title: str
    data: Optional[dict] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)

class CanvasForm(BaseModel):
    title: Optional[str] = None
    data: Optional[dict] = None
    chat_id: Optional[str] = None

# Pydantic models for AI interaction
class CanvasProcessRequest(BaseModel):
    content: str | dict # Using Union via | for Python 3.10+
    command: str
    model_id: Optional[str] = None

class CanvasProcessResponse(BaseModel):
    processed_content: str

class CanvasTable:
    def insert_new_canvas(
        self, user_id: str, form_data: CanvasForm
    ) -> Optional[CanvasModel]:
        with get_db() as db:
            canvas = Canvas(
                user_id=user_id,
                title=form_data.title if form_data.title else "Untitled Canvas",
                data=form_data.data if form_data.data else {},
                chat_id=form_data.chat_id,
            )
            db.add(canvas)
            db.commit()
            db.refresh(canvas)
            return CanvasModel.model_validate(canvas)

    def get_canvas_by_id(
        self, canvas_id: str, user_id: str
    ) -> Optional[CanvasModel]:
        with get_db() as db:
            canvas = (
                db.query(Canvas)
                .filter_by(id=canvas_id, user_id=user_id)
                .first()
            )
            if canvas:
                return CanvasModel.model_validate(canvas)
            return None

    def get_canvases_by_user_id(self, user_id: str) -> List[CanvasModel]:
        with get_db() as db:
            canvases = db.query(Canvas).filter_by(user_id=user_id).all()
            return [CanvasModel.model_validate(canvas) for canvas in canvases]

    def update_canvas_by_id(
        self, canvas_id: str, user_id: str, form_data: CanvasForm
    ) -> Optional[CanvasModel]:
        with get_db() as db:
            canvas = (
                db.query(Canvas)
                .filter_by(id=canvas_id, user_id=user_id)
                .first()
            )
            if canvas:
                if form_data.title is not None:
                    canvas.title = form_data.title
                if form_data.data is not None:
                    canvas.data = form_data.data
                if form_data.chat_id is not None:
                    canvas.chat_id = form_data.chat_id
                db.commit()
                db.refresh(canvas)
                return CanvasModel.model_validate(canvas)
            return None

    def delete_canvas_by_id(self, canvas_id: str, user_id: str) -> bool:
        with get_db() as db:
            canvas = (
                db.query(Canvas)
                .filter_by(id=canvas_id, user_id=user_id)
                .first()
            )
            if canvas:
                db.delete(canvas)
                db.commit()
                return True
            return False

Canvases = CanvasTable()
