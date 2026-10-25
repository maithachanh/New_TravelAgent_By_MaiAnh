import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.request_parser import parse_travel_request

logger = logging.getLogger("LLMService")

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self.model_name = settings.OPENAI_MODEL or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def is_available(self) -> bool:
        """Check if a non-placeholder OpenAI API key is configured."""
        if not self.api_key or len(self.api_key.strip()) < 20:
            return False
        if "your_" in self.api_key.lower() or "dummy" in self.api_key.lower():
            return False
        return True

    def extract_travel_requirements(self, prompt: str) -> Dict[str, Any]:
        """
        Hybrid Requirements Extractor:
        1. If OpenAI API key is available, queries OpenAI for deep natural language understanding.
        2. If API key is absent or OpenAI call fails/times out, seamlessly uses the high-precision
           deterministic parse_travel_request engine.
        """
        if not self.is_available():
            return parse_travel_request(prompt)

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.0,
                timeout=12.0
            )

            system_instruction = (
                "You are an expert multilingual AI travel assistant. Analyze the user prompt and extract travel parameters in JSON format. "
                "Keys must include: "
                "'destination' (string, e.g. 'Tokyo, Nhật Bản'), "
                "'origin' (string, e.g. 'Thành phố Hồ Chí Minh, Việt Nam' or 'Hà Nội, Việt Nam'), "
                "'duration' (integer number of days, e.g. 5), "
                "'budget' (number in local currency/VND), "
                "'currency' (string, e.g. 'VND', 'USD', 'JPY', 'GBP', 'EUR'), "
                "'travelers' (integer number of people), "
                "'preferences' (array of strings, e.g. ['ẩm thực', 'văn hóa']), "
                "'start_date' (optional string YYYY-MM-DD or null), "
                "'end_date' (optional string YYYY-MM-DD or null), "
                "'intent' (string: 'PLAN_NEW_TRIP', 'REPLAN_TRIP', 'IN_TRIP_SUPPORT'). "
                "Respond ONLY with valid JSON."
            )

            response = llm.invoke([
                SystemMessage(content=system_instruction),
                HumanMessage(content=prompt)
            ])

            raw_text = response.content.strip()
            # Clean markdown formatting if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed = json.loads(raw_text.strip())
            # Ensure critical fallback defaults
            fallback = parse_travel_request(prompt)
            return {
                "destination": parsed.get("destination") or fallback.get("destination"),
                "origin": parsed.get("origin") or fallback.get("origin"),
                "duration": int(parsed.get("duration") or fallback.get("duration", 4)),
                "budget": float(parsed.get("budget") or fallback.get("budget", 30000000.0)),
                "currency": parsed.get("currency") or fallback.get("currency", "VND"),
                "travelers": int(parsed.get("travelers") or fallback.get("travelers", 2)),
                "preferences": parsed.get("preferences") or fallback.get("preferences", []),
                "start_date": parsed.get("start_date") or fallback.get("start_date"),
                "end_date": parsed.get("end_date") or fallback.get("end_date"),
                "intent": parsed.get("intent") or fallback.get("intent", "PLAN_NEW_TRIP")
            }

        except Exception as e:
            logger.warning(f"OpenAI extraction failed ({e}), falling back to deterministic parser")
            return parse_travel_request(prompt)

    def enhance_trip_narrative(self, destination: str, duration: int, preferences: list) -> Optional[str]:
        """Provides AI-generated contextual advice when LLM is available."""
        if not self.is_available():
            return None
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage

            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.7,
                timeout=10.0
            )
            msg = HumanMessage(
                content=f"Hãy viết lời chào và 3 lời khuyên đặc biệt hữu ích bằng tiếng Việt cho chuyến du lịch {destination} trong {duration} ngày với sở thích: {', '.join(preferences)}."
            )
            resp = llm.invoke([msg])
            return resp.content.strip()
        except Exception:
            return None

llm_service = LLMService()
