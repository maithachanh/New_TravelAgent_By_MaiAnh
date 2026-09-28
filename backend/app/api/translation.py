from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.translation_service import translation_service

router = APIRouter(prefix="/translation", tags=["Multi-language Translation"])

class TranslationRequest(BaseModel):
    text: str
    target_lang: Optional[str] = None
    target_language: Optional[str] = None
    source_lang: Optional[str] = "auto"
    source_language: Optional[str] = "auto"

@router.post("/translate")
def translate_text(req: TranslationRequest):
    tl = req.target_lang or req.target_language or "en"
    sl = req.source_lang or req.source_language or "auto"
    return translation_service.translate(
        text=req.text,
        target_lang=tl,
        source_lang=sl
    )
