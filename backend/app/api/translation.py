from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.translation_service import translation_service

router = APIRouter(prefix="/translation", tags=["Multi-language Translation"])

class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5_000)
    target_lang: Optional[str] = None
    target_language: Optional[str] = None
    source_lang: Optional[str] = None
    source_language: Optional[str] = None

@router.post("/translate")
def translate_text(req: TranslationRequest):
    tl = req.target_lang or req.target_language or "en"
    sl = req.source_lang or req.source_language or "auto"
    try:
        return translation_service.translate(text=req.text, target_lang=tl, source_lang=sl)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
