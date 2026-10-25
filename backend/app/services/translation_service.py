"""Translation providers with an honest, useful offline travel fallback."""

from __future__ import annotations

import os
import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests


LANGUAGE_ALIASES = {
    "vietnamese": "vi", "english": "en", "korean": "ko", "japanese": "ja",
    "french": "fr", "german": "de", "spanish": "es", "italian": "it",
    "thai": "th", "chinese": "zh-CN", "mandarin": "zh-CN",
    "russian": "ru", "portuguese": "pt", "arabic": "ar", "hindi": "hi",
    "bengali": "bn", "turkish": "tr", "polish": "pl", "dutch": "nl",
    "swedish": "sv", "norwegian": "no", "danish": "da", "finnish": "fi",
    "greek": "el", "hebrew": "he", "indonesian": "id", "malay": "ms",
    "filipino": "tl", "czech": "cs", "romanian": "ro", "hungarian": "hu",
    "ukrainian": "uk", "viet": "vi", "vn": "vi", "jp": "ja", "kr": "ko",
    "cn": "zh-CN", "tw": "zh-TW", "hk": "zh-HK", "sg": "zh-SG",
}


def normalise_language(code: Optional[str], *, allow_auto: bool = True) -> str:
    value = (code or ("auto" if allow_auto else "en")).strip().lower().replace("_", "-")
    value = LANGUAGE_ALIASES.get(value, value)
    if value == "auto" and allow_auto:
        return value
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z]{2,4})?", value):
        raise ValueError("Language must be an ISO 639 code, for example 'vi' or 'en'.")
    return value


def _normalise_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").replace("đ", "d")


class BaseTranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        raise NotImplementedError


class OnlineTranslationProvider(BaseTranslationProvider):
    """Try public providers while keeping their failures isolated from the API."""

    def translate(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        # Try Google Translate API first
        try:
            response = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": source_lang, "tl": target_lang, "dt": "t", "q": text},
                headers={"User-Agent": "TravelAgentAI/2.1"},
                timeout=5.0,
            )
            if response.ok:
                data = response.json()
                chunks = data[0] if isinstance(data, list) and data else []
                translated = "".join(part[0] for part in chunks if part and part[0])
                if translated and translated != text:  # Ensure translation actually happened
                    detected = data[2] if len(data) > 2 and isinstance(data[2], str) else source_lang
                    return {
                        "translated_text": translated,
                        "source_lang": detected,
                        "target_lang": target_lang,
                        "provider": "Google Translate",
                        "success": True,
                    }
        except (requests.RequestException, ValueError, TypeError, IndexError):
            pass

        # Try MyMemory as fallback (requires concrete source language)
        if source_lang != "auto":
            try:
                response = requests.get(
                    "https://api.mymemory.translated.net/get",
                    params={"q": text, "langpair": f"{source_lang}|{target_lang}"},
                    timeout=5.0,
                )
                if response.ok:
                    translated = response.json().get("responseData", {}).get("translatedText")
                    if translated and not translated.startswith("MYMEMORY WARNING") and translated != text:
                        return {
                            "translated_text": translated,
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                            "provider": "MyMemory",
                            "success": True,
                        }
            except (requests.RequestException, ValueError, TypeError):
                pass

        # Try LibreTranslate as another fallback
        try:
            response = requests.post(
                "https://libretranslate.com/translate",
                json={"q": text, "source": source_lang if source_lang != "auto" else "auto", "target": target_lang},
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            if response.ok:
                translated = response.json().get("translatedText")
                if translated and translated != text:
                    return {
                        "translated_text": translated,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "provider": "LibreTranslate",
                        "success": True,
                    }
        except (requests.RequestException, ValueError, TypeError):
            pass

        return OfflineTravelPhraseProvider().translate(text, target_lang, source_lang)


class DeepLTranslationProvider(BaseTranslationProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def translate(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        try:
            payload: Dict[str, Any] = {"text": [text], "target_lang": target_lang.upper()}
            if source_lang != "auto":
                payload["source_lang"] = source_lang.upper()
            response = requests.post(
                "https://api-free.deepl.com/v2/translate",
                headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                json=payload,
                timeout=5.0,
            )
            if response.ok:
                translation = response.json()["translations"][0]
                return {
                    "translated_text": translation["text"],
                    "source_lang": translation.get("detected_source_language", source_lang).lower(),
                    "target_lang": target_lang,
                    "provider": "DeepL",
                    "success": True,
                }
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
            pass
        return OnlineTranslationProvider().translate(text, target_lang, source_lang)


class OfflineTravelPhraseProvider(BaseTranslationProvider):
    """Small no-network safety net for the travel phrases shown in the UI."""

    PHRASES: Dict[str, Dict[str, str]] = {
        "xin chao": {"en": "Hello", "de": "Hallo", "fr": "Bonjour", "es": "Hola", "it": "Ciao", "ja": "こんにちは", "ko": "안녕하세요", "th": "สวัสดี", "zh-CN": "你好", "ru": "Привет"},
        "cam on": {"en": "Thank you", "de": "Danke", "fr": "Merci", "es": "Gracias", "it": "Grazie", "ja": "ありがとうございます", "ko": "감사합니다", "th": "ขอบคุณ", "zh-CN": "谢谢", "ru": "Спасибо"},
        "tam biet": {"en": "Goodbye", "de": "Auf Wiedersehen", "fr": "Au revoir", "es": "Adiós", "it": "Arrivederci", "ja": "さようなら", "ko": "안녕히 계세요", "th": "ลาก่อน", "zh-CN": "再见", "ru": "До свидания"},
        "bao nhieu tien": {"en": "How much is it?", "de": "Wie viel kostet das?", "fr": "Combien ça coûte ?", "ja": "いくらですか？", "ko": "얼마예요?", "th": "ราคาเท่าไหร่?", "zh-CN": "多少钱？", "ru": "Сколько это стоит?"},
        "bao nhieu tien mot dem": {"en": "How much is one night?", "de": "Wie viel kostet eine Nacht?", "ja": "一泊はいくらですか？", "ko": "하룻밤에 얼마인가요?", "th": "ราคาคืนละเท่าไหร่?", "zh-CN": "一晚多少钱？", "ru": "Сколько стоит ночь?"},
        "cho toi xem thuc don": {"en": "May I see the menu?", "de": "Kann ich die Speisekarte sehen?", "ja": "メニューを見せてください。", "ko": "메뉴를 볼 수 있을까요?", "th": "ขอดูเมนูได้ไหม?", "zh-CN": "可以给我看菜单吗？", "ru": "Можно посмотреть меню?"},
        "tinh tien": {"en": "The bill, please.", "de": "Die Rechnung, bitte.", "fr": "L'addition, s'il vous plaît.", "ja": "お会計をお願いします。", "ko": "계산서 부탁드립니다.", "th": "คิดเงินให้หน่อย", "zh-CN": "请结账", "ru": "Счет, пожалуйста"},
        "toi can giup do khan cap": {"en": "I need emergency help.", "de": "Ich brauche dringend Hilfe.", "ja": "緊急の助けが必要です。", "ko": "긴급한 도움이 필요합니다.", "th": "ฉันต้องการความช่วยเหลือฉุกเฉิน", "zh-CN": "我需要紧急帮助", "ru": "Мне нужна экстренная помощь"},
        "san bay o dau": {"en": "Where is the airport?", "de": "Wo ist der Flughafen?", "ja": "空港はどこですか？", "ko": "공항이 어디에 있나요?", "th": "สนามบินอยู่ที่ไหน?", "zh-CN": "机场在哪里？", "ru": "Где находится аэропорт?"},
        "ga tau o dau": {"en": "Where is the train station?", "de": "Wo ist der Bahnhof?", "ja": "駅はどこですか？", "ko": "기차역이 어디에 있나요?", "th": "สถานีรถไฟอยู่ที่ไหน?", "zh-CN": "火车站在哪里？", "ru": "Где находится вокзал?"},
        "toilet o dau": {"en": "Where is the restroom?", "de": "Wo ist die Toilette?", "fr": "Où sont les toilettes?", "ja": "トイレはどこですか？", "ko": "화장실이 어디에 있나요?", "th": "ห้องน้ำอยู่ที่ไหน?", "zh-CN": "洗手间在哪里？", "ru": "Где туалет?"},
        "khong hieu": {"en": "I don't understand", "de": "Ich verstehe nicht", "fr": "Je ne comprends pas", "ja": "わかりません", "ko": "이해하지 못해요", "th": "ฉันไม่เข้าใจ", "zh-CN": "我不明白", "ru": "Я не понимаю"},
        "ban co tieng viet khong": {"en": "Do you speak Vietnamese?", "de": "Sprechen Sie Vietnamesisch?", "fr": "Parlez-vous vietnamien?", "ja": "ベトナム語を話せますか？", "ko": "베트남어 하시나요?", "th": "คุณพูดภาษาเวียดนามได้ไหม?", "zh-CN": "你会说越南语吗？", "ru": "Вы говорите по-вьетнамски?"},
        "hello": {"vi": "Xin chào", "de": "Hallo", "fr": "Bonjour", "es": "Hola", "it": "Ciao", "ja": "こんにちは", "ko": "안녕하세요", "th": "สวัสดี", "zh-CN": "你好", "ru": "Привет"},
        "thank you": {"vi": "Cảm ơn", "de": "Danke", "fr": "Merci", "es": "Gracias", "it": "Grazie", "ja": "ありがとうございます", "ko": "감사합니다", "th": "ขอบคุณ", "zh-CN": "谢谢", "ru": "Спасибо"},
        "goodbye": {"vi": "Tạm biệt", "de": "Auf Wiedersehen", "fr": "Au revoir", "es": "Adiós", "it": "Arrivederci", "ja": "さようなら", "ko": "안녕히 계세요", "th": "ลาก่อน", "zh-CN": "再见", "ru": "До свидания"},
        "how much is it": {"vi": "Bao nhiêu tiền?", "de": "Wie viel kostet das?", "fr": "Combien ça coûte ?", "ja": "いくらですか？", "ko": "얼마예요?", "th": "ราคาเท่าไหร่?", "zh-CN": "多少钱？", "ru": "Сколько это стоит?"},
        "how much is one night": {"vi": "Bao nhiêu tiền một đêm?", "de": "Wie viel kostet eine Nacht?", "ja": "一泊はいくらですか？", "ko": "하룻밤에 얼마인가요?", "th": "ราคาคืนละเท่าไหร่?", "zh-CN": "一晚多少钱？", "ru": "Сколько стоит ночь?"},
        "may i see the menu": {"vi": "Cho tôi xem thực đơn", "de": "Kann ich die Speisekarte sehen?", "ja": "メニューを見せてください。", "ko": "메뉴를 볼 수 있을까요?", "th": "ขอดูเมนูได้ไหม?", "zh-CN": "可以给我看菜单吗？", "ru": "Можно посмотреть меню?"},
        "the bill please": {"vi": "Tính tiền", "de": "Die Rechnung, bitte.", "fr": "L'addition, s'il vous plaît.", "ja": "お会計をお願いします。", "ko": "계산서 부탁드립니다.", "th": "คิดเงินให้หน่อย", "zh-CN": "请结账", "ru": "Счет, пожалуйста"},
        "i need emergency help": {"vi": "Tôi cần giúp đỡ khẩn cấp", "de": "Ich brauche dringend Hilfe.", "ja": "緊急の助けが必要です。", "ko": "긴급한 도움이 필요합니다.", "th": "ฉันต้องการความช่วยเหลือฉุกเฉิน", "zh-CN": "我需要紧急帮助", "ru": "Мне нужна экстренная помощь"},
        "where is the airport": {"vi": "Sân bay ở đâu?", "de": "Wo ist der Flughafen?", "ja": "空港はどこですか？", "ko": "공항이 어디에 있나요?", "th": "สนามบินอยู่ที่ไหน?", "zh-CN": "机场在哪里？", "ru": "Где находится аэропорт?"},
        "where is the train station": {"vi": "Ga tàu ở đâu?", "de": "Wo ist der Bahnhof?", "ja": "駅はどこですか？", "ko": "기차역이 어디에 있나요?", "th": "สถานีรถไฟอยู่ที่ไหน?", "zh-CN": "火车站在哪里？", "ru": "Где находится вокзал?"},
    }

    def translate(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        text_lower = text.lower().strip(" ?!.,")
        for phrase, translations in self.PHRASES.items():
            phrase_lower = phrase.lower().strip(" ?!.,")
            if text_lower == phrase_lower or phrase_lower in text_lower or text_lower in phrase_lower:
                translated = translations.get(target_lang, translations.get("en"))
                if translated:
                    return {
                        "translated_text": translated,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "provider": "Offline travel phrases",
                        "success": True,
                    }
        return {
            "translated_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "provider": "offline fallback",
            "success": False,
            "error": "Translation provider is unavailable. Check the network and try again.",
        }


class UniversalTranslationService:
    def __init__(self) -> None:
        deepl_key = os.getenv("DEEPL_API_KEY", "").strip()
        self.provider: BaseTranslationProvider = DeepLTranslationProvider(deepl_key) if deepl_key else OnlineTranslationProvider()

    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = "auto") -> Dict[str, Any]:
        clean_text = text.strip()
        if not clean_text:
            return {"translated_text": "", "source_lang": source_lang or "auto", "target_lang": target_lang, "provider": "none", "success": True}
        return self.provider.translate(clean_text, normalise_language(target_lang, allow_auto=False), normalise_language(source_lang))


translation_service = UniversalTranslationService()
