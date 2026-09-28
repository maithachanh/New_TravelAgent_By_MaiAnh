import os
import requests
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseTranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        pass

class GoogleFreeTranslationProvider(BaseTranslationProvider):
    """
    High-availability, zero-configuration online translation engine
    supporting 100+ languages without API keys.
    """
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        if not text or not text.strip():
            return {"translated_text": "", "source_lang": source_lang, "target_lang": target_lang, "provider": "Empty"}
        
        sl = (source_lang or "auto").lower().strip()
        tl = (target_lang or "en").lower().strip()
        
        # Normalize language codes
        lang_map = {
            "vi": "vi", "vietnamese": "vi",
            "en": "en", "english": "en",
            "ko": "ko", "korean": "ko",
            "ja": "ja", "japanese": "ja",
            "fr": "fr", "french": "fr",
            "de": "de", "german": "de",
            "es": "es", "spanish": "es",
            "it": "it", "italian": "it",
            "th": "th", "thai": "th",
            "zh": "zh-CN", "chinese": "zh-CN"
        }
        tl = lang_map.get(tl, tl)
        if sl != "auto":
            sl = lang_map.get(sl, sl)

        # 1. Primary: Google Free Web Translate endpoint
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": sl,
                "tl": tl,
                "dt": "t",
                "q": text
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(url, params=params, headers=headers, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    translated_chunks = [segment[0] for segment in data[0] if segment and segment[0]]
                    translated_text = "".join(translated_chunks)
                    detected_src = data[2] if len(data) > 2 and isinstance(data[2], str) else sl
                    return {
                        "translated_text": translated_text,
                        "source_lang": detected_src,
                        "target_lang": tl,
                        "provider": "GoogleTranslateEngine"
                    }
        except Exception:
            pass

        # 2. Secondary fallback: MyMemory Translation API
        try:
            pair = f"{sl}|{tl}" if sl != "auto" else f"vi|{tl}"
            mm_url = "https://api.mymemory.translated.net/get"
            mm_resp = requests.get(mm_url, params={"q": text, "langpair": pair}, timeout=3.5)
            if mm_resp.status_code == 200:
                mm_data = mm_resp.json()
                t_res = mm_data.get("responseData", {}).get("translatedText")
                if t_res and not t_res.startswith("MYMEMORY WARNING"):
                    return {
                        "translated_text": t_res,
                        "source_lang": sl,
                        "target_lang": tl,
                        "provider": "MyMemoryAPI"
                    }
        except Exception:
            pass

        # 3. Tertiary fallback: Smart Local Travel Phrase Dictionary
        return SmartLocalTranslationProvider().translate(text, tl, sl)

class DeepLTranslationProvider(BaseTranslationProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        try:
            url = "https://api-free.deepl.com/v2/translate"
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            payload = {"text": [text], "target_lang": target_lang.upper()}
            resp = requests.post(url, headers=headers, json=payload, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                translated = data["translations"][0]["text"]
                return {"translated_text": translated, "provider": "DeepL API", "target_lang": target_lang}
        except Exception:
            pass
        return GoogleFreeTranslationProvider().translate(text, target_lang, source_lang)

class SmartLocalTranslationProvider(BaseTranslationProvider):
    DICTIONARY = {
        # Common Travel Phrases
        "xin chào": {"en": "Hello", "de": "Hallo", "ko": "안녕하세요", "ja": "こんにちは", "fr": "Bonjour", "it": "Ciao", "es": "Hola"},
        "cảm ơn": {"en": "Thank you", "de": "Danke", "ko": "감사합니다", "ja": "ありがとうございます", "fr": "Merci", "it": "Grazie", "es": "Gracias"},
        "tạm biệt": {"en": "Goodbye", "de": "Auf Wiedersehen", "ko": "안녕히 계세요", "ja": "さようなら", "fr": "Au revoir", "it": "Arrivederci", "es": "Adiós"},
        "bao nhiêu tiền": {"en": "How much is it?", "de": "Wie viel kostet das?", "ko": "얼마예요?", "ja": "いくらですか？", "fr": "Combien ça coûte?", "it": "Quanto costa?", "es": "¿Cuánto cuesta?"},
        "bao nhiêu tiền một đêm": {"en": "How much per night?", "de": "Wie viel kostet eine Nacht?", "ko": "하룻밤에 얼마인가요?", "ja": "一泊いくらですか？", "fr": "Combien par nuit?", "it": "Quanto a notte?", "es": "¿Cuánto por noche?"},
        "tính tiền": {"en": "Check, please", "de": "Die Rechnung, bitte", "ko": "계산해 주세요", "ja": "お会計をお願いします", "fr": "L'addition, s'il vous plaît", "it": "Il conto, per favore", "es": "La cuenta, por favor"},
        "làm ơn": {"en": "Please", "de": "Bitte", "ko": "부탁합니다", "ja": "お願いします", "fr": "S'il vous plaît", "it": "Per favore", "es": "Por favor"},
        "cứu tôi với": {"en": "Help me!", "de": "Hilfe!", "ko": "도와주세요!", "ja": "助けてください！", "fr": "Aidez-moi!", "it": "Aiuto!", "es": "¡Ayuda!"},
        "tôi cần giúp đỡ khẩn cấp": {"en": "I need emergency assistance!", "de": "Ich brauche dringend Notfallhilfe!", "ko": "긴급 지원이 필요합니다!", "ja": "緊急の助けが必要です！", "fr": "J'ai besoin d'une aide d'urgence!", "it": "Ho bisogno di aiuto urgente!", "es": "¡Necesito ayuda de emergencia!"},
        "ga tàu": {"en": "Train station", "de": "Bahnhof", "ko": "기차역", "ja": "駅", "fr": "Gare", "it": "Stazione ferroviaria", "es": "Estación de tren"},
        "sân bay": {"en": "Airport", "de": "Flughafen", "ko": "공항", "ja": "空港", "fr": "Aéroport", "it": "Aeroporto", "es": "Aeropuerto"},
        "khách sạn": {"en": "Hotel", "de": "Hotel", "ko": "호텔", "ja": "ホテル", "fr": "Hôtel", "it": "Hotel", "es": "Hotel"},
        "nhà hàng": {"en": "Restaurant", "de": "Restaurant", "ko": "식당", "ja": "レストラン", "fr": "Restaurant", "it": "Ristorante", "es": "Restaurante"},
        "chuyến bay": {"en": "Flight", "de": "Flug", "ko": "항공편", "ja": "フライト", "fr": "Vol", "it": "Volo", "es": "Vuelo"},
        "bữa trưa": {"en": "Lunch", "de": "Mittagessen", "ko": "점심 식사", "ja": "昼食", "fr": "Déjeuner", "it": "Pranzo", "es": "Almuerzo"},
        "bữa tối": {"en": "Dinner", "de": "Abendessen", "ko": "저녁 식사", "ja": "夕食", "fr": "Dîner", "it": "Cena", "es": "Cena"},
        "thực đơn": {"en": "Menu", "de": "Speisekarte", "ko": "메뉴", "ja": "メニュー", "fr": "Menu", "it": "Menu", "es": "Menú"},
        "món chay": {"en": "Vegetarian food", "de": "Vegetarisches Essen", "ko": "채식", "ja": "ベジタリアン料理", "fr": "Plat végétarien", "it": "Cibo vegetariano", "es": "Comida vegetariana"}
    }

    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        target = target_lang.lower().strip()
        t_clean = text.lower().strip()
        
        for key, trans_map in self.DICTIONARY.items():
            if key in t_clean:
                translated = trans_map.get(target, trans_map.get("en", text))
                return {
                    "translated_text": translated,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "provider": "SmartLocalDictionary"
                }

        return {
            "translated_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "provider": "LocalEchoFallback"
        }

class UniversalTranslationService:
    def __init__(self):
        deepl_key = os.getenv("DEEPL_API_KEY", "")
        if deepl_key:
            self.provider: BaseTranslationProvider = DeepLTranslationProvider(deepl_key)
        else:
            self.provider: BaseTranslationProvider = GoogleFreeTranslationProvider()

    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        return self.provider.translate(text, target_lang, source_lang)

translation_service = UniversalTranslationService()
