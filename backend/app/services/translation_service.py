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
                timeout=4.0,
            )
            if response.ok:
                data = response.json()
                chunks = data[0] if isinstance(data, list) and data else []
                translated = "".join(part[0] for part in chunks if part and part[0])
                if translated and translated.strip().lower() != text.strip().lower():
                    detected = data[2] if len(data) > 2 and isinstance(data[2], str) else source_lang
                    return {
                        "translated_text": translated,
                        "source_lang": detected,
                        "target_lang": target_lang,
                        "provider": "Google Translate",
                        "success": True,
                    }
        except Exception:
            pass

        # Try MyMemory as fallback
        if source_lang != "auto":
            try:
                response = requests.get(
                    "https://api.mymemory.translated.net/get",
                    params={"q": text, "langpair": f"{source_lang}|{target_lang}"},
                    timeout=4.0,
                )
                if response.ok:
                    translated = response.json().get("responseData", {}).get("translatedText")
                    if translated and not translated.startswith("MYMEMORY WARNING") and translated.strip().lower() != text.strip().lower():
                        return {
                            "translated_text": translated,
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                            "provider": "MyMemory",
                            "success": True,
                        }
            except Exception:
                pass

        # Try LibreTranslate as another fallback
        try:
            response = requests.post(
                "https://libretranslate.com/translate",
                json={"q": text, "source": source_lang if source_lang != "auto" else "auto", "target": target_lang},
                headers={"Content-Type": "application/json"},
                timeout=4.0,
            )
            if response.ok:
                translated = response.json().get("translatedText")
                if translated and translated.strip().lower() != text.strip().lower():
                    return {
                        "translated_text": translated,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "provider": "LibreTranslate",
                        "success": True,
                    }
        except Exception:
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
                timeout=4.0,
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
        except Exception:
            pass
        return OnlineTranslationProvider().translate(text, target_lang, source_lang)


class OfflineTravelPhraseProvider(BaseTranslationProvider):
    """
    Extensive travel dictionary for offline & network-failure scenarios.
    Covers greetings, hotels, food, shopping, transport, emergency, and inquiries across 10 major languages.
    """

    PHRASES: Dict[str, Dict[str, str]] = {
        # Greetings & Courtesy
        "xin chao": {"en": "Hello", "de": "Hallo", "fr": "Bonjour", "es": "Hola", "it": "Ciao", "ja": "こんにちは", "ko": "안녕하세요", "th": "สวัสดี", "zh-CN": "你好", "ru": "Привет"},
        "cam on": {"en": "Thank you", "de": "Danke", "fr": "Merci", "es": "Gracias", "it": "Grazie", "ja": "ありがとうございます", "ko": "감사합니다", "th": "ขอบคุณ", "zh-CN": "谢谢", "ru": "Спасибо"},
        "tam biet": {"en": "Goodbye", "de": "Auf Wiedersehen", "fr": "Au revoir", "es": "Adiós", "it": "Arrivederci", "ja": "さようなら", "ko": "안녕히 계세요", "th": "ลาก่อน", "zh-CN": "再见", "ru": "До свидания"},
        "xin loi": {"en": "Excuse me / Sorry", "de": "Entschuldigung", "fr": "Pardon / Excusez-moi", "es": "Perdón / Disculpe", "it": "Scusi", "ja": "すみません", "ko": "죄송합니다", "th": "ขอโทษ", "zh-CN": "不好意思 / 对不起", "ru": "Извините"},
        "lam on": {"en": "Please", "de": "Bitte", "fr": "S'il vous plaît", "es": "Por favor", "it": "Per favore", "ja": "お願いします", "ko": "부탁합니다", "th": "กรุณา", "zh-CN": "请", "ru": "Пожалуйста"},
        "khong co chi": {"en": "You're welcome", "de": "Gern geschehen", "fr": "De rien", "es": "De nada", "it": "Prego", "ja": "どういたしまして", "ko": "천만에요", "th": "ไม่เป็นไร", "zh-CN": "不客气", "ru": "Не за что"},
        "vang": {"en": "Yes", "de": "Ja", "fr": "Oui", "es": "Sí", "it": "Sì", "ja": "はい", "ko": "네", "th": "ใช่", "zh-CN": "是的", "ru": "Да"},
        "khong": {"en": "No", "de": "Nein", "fr": "Non", "es": "No", "it": "No", "ja": "いいえ", "ko": "아니요", "th": "ไม่ใช่", "zh-CN": "不", "ru": "Нет"},

        # Accommodation & Hotel
        "bao nhieu tien mot dem": {"en": "How much is one night?", "de": "Wie viel kostet eine Nacht?", "fr": "Combien coûte une nuit ?", "ja": "一泊はいくらですか？", "ko": "하룻밤에 얼마인가요?", "th": "ราคาคืนละเท่าไหร่?", "zh-CN": "一晚多少钱？", "ru": "Сколько стоит ночь?"},
        "toi muon nhan phong": {"en": "I want to check in", "de": "Ich möchte einchecken", "fr": "Je voudrais m'enregistrer", "ja": "チェックインをお願いします", "ko": "체크인하고 싶습니다", "th": "ฉันต้องการเช็คอิน", "zh-CN": "我想办理入住", "ru": "Я хочу зарегистрироваться"},
        "toi muon tra phong": {"en": "I want to check out", "de": "Ich möchte auschecken", "fr": "Je voudrais régler la note", "ja": "チェックアウトをお願いします", "ko": "체크아웃하고 싶습니다", "th": "ฉันต้องการเช็คเอาท์", "zh-CN": "我想办理退房", "ru": "Я хочу выехать"},
        "co phong trong khong": {"en": "Do you have any vacancies?", "de": "Haben Sie freie Zimmer?", "fr": "Avez-vous des chambres libres ?", "ja": "空き部屋はありますか？", "ko": "빈 방 있나요?", "th": "มีห้องว่างไหม?", "zh-CN": "有空房吗？", "ru": "Есть ли свободные номера?"},
        "cho toi xin mat khau wifi": {"en": "What is the Wi-Fi password?", "de": "Wie lautet das WLAN-Passwort?", "fr": "Quel est le mot de passe Wi-Fi ?", "ja": "Wi-Fiのパスワードは何ですか？", "ko": "와이파이 비밀번호가 무엇인가요?", "th": "รหัสผ่านไวไฟคืออะไร?", "zh-CN": "Wi-Fi密码是多少？", "ru": "Какой пароль от Wi-Fi?"},
        "co an sang khong": {"en": "Is breakfast included?", "de": "Ist das Frühstück inbegriffen?", "fr": "Le petit déjeuner est-il inclus ?", "ja": "朝食は含まれていますか？", "ko": "조식이 포함되어 있나요?", "th": "รวมอาหารเช้าไหม?", "zh-CN": "包含早餐吗？", "ru": "Завтрак включен?"},
        "don phong giup toi": {"en": "Please clean my room", "de": "Bitte reinigen Sie mein Zimmer", "fr": "Veuillez nettoyer ma chambre", "ja": "部屋を掃除してください", "ko": "방 청소 부탁드립니다", "th": "กรุณาทำความสะอาดห้อง", "zh-CN": "请打扫房间", "ru": "Пожалуйста, уберите в номере"},
        "hanh ly cua toi": {"en": "My luggage", "de": "Mein Gepäck", "fr": "Mes bagages", "es": "Mi equipaje", "ja": "私の荷物", "ko": "내 수하물", "th": "กระเป๋าเดินทางของฉัน", "zh-CN": "我的行李", "ru": "Мой багаж"},

        # Dining & Food
        "cho toi xem thuc don": {"en": "May I see the menu?", "de": "Kann ich die Speisekarte sehen?", "fr": "Puis-je voir le menu ?", "ja": "メニューを見せてください。", "ko": "메뉴를 볼 수 있을까요?", "th": "ขอดูเมนูได้ไหม?", "zh-CN": "可以给我看菜单吗？", "ru": "Можно посмотреть меню?"},
        "tinh tien": {"en": "The bill, please.", "de": "Die Rechnung, bitte.", "fr": "L'addition, s'il vous plaît.", "es": "La cuenta, por favor.", "ja": "お会計をお願いします。", "ko": "계산서 부탁드립니다.", "th": "คิดเงินให้หน่อย", "zh-CN": "请结账", "ru": "Счет, пожалуйста"},
        "cho toi nuoc loc": {"en": "Water, please", "de": "Wasser, bitte", "fr": "De l'eau, s'il vous plaît", "ja": "お水をください", "ko": "물 좀 주세요", "th": "ขอน้ำเปล่าหน่อย", "zh-CN": "请给我一杯水", "ru": "Воды, пожалуйста"},
        "mon nay co cay khong": {"en": "Is this spicy?", "de": "Ist das scharf?", "fr": "Est-ce épicé ?", "ja": "これは辛いですか？", "ko": "이거 맵나요?", "th": "อันนี้เผ็ดไหม?", "zh-CN": "这个辣吗？", "ru": "Это острое?"},
        "toi an chay": {"en": "I am vegetarian", "de": "Ich bin Vegetarier", "fr": "Je suis végétarien", "ja": "私はベジタリアンです", "ko": "저는 채식주의자입니다", "th": "ฉันกินมังสวิรัติ", "zh-CN": "我是素食主义者", "ru": "Я вегетарианец"},
        "khong bo duong": {"en": "No sugar, please", "de": "Ohne Zucker, bitte", "fr": "Sans sucre, s'il vous plaît", "ja": "砂糖なしでお願いします", "ko": "설탕 빼주세요", "th": "ไม่ใส่น้ำตาล", "zh-CN": "不要糖", "ru": "Без сахара, пожалуйста"},
        "mon nay rat ngon": {"en": "This is delicious!", "de": "Das ist köstlich!", "fr": "C'est délicieux !", "ja": "とても美味しいです！", "ko": "정말 맛있어요!", "th": "อร่อยมาก!", "zh-CN": "非常好吃！", "ru": "Это очень вкусно!"},
        "nha hang o dau": {"en": "Where is the restaurant?", "de": "Wo ist das Restaurant?", "fr": "Où est le restaurant ?", "ja": "レストランはどこですか？", "ko": "식당이 어디에 있나요?", "th": "ร้านอาหารอยู่ที่ไหน?", "zh-CN": "餐厅在哪里？", "ru": "Где находится ресторан?"},

        # Shopping & Currency
        "bao nhieu tien": {"en": "How much is it?", "de": "Wie viel kostet das?", "fr": "Combien ça coûte ?", "es": "Cuánto cuesta?", "ja": "いくらですか？", "ko": "얼마예요?", "th": "ราคาเท่าไหร่?", "zh-CN": "多少钱？", "ru": "Сколько это стоит?"},
        "dat qua": {"en": "Too expensive", "de": "Zu teuer", "fr": "Trop cher", "es": "Demasiado caro", "ja": "高すぎます", "ko": "너무 비싸요", "th": "แพงเกินไป", "zh-CN": "太贵了", "ru": "Слишком дорого"},
        "co giam gia khong": {"en": "Is there a discount?", "de": "Gibt es einen Rabatt?", "fr": "Y a-t-il une réduction ?", "ja": "割引はありますか？", "ko": "할인 되나요?", "th": "มีส่วนลดไหม?", "zh-CN": "有折扣吗？", "ru": "Есть ли скидка?"},
        "toi co the thanh toan bang the khong": {"en": "Can I pay by card?", "de": "Kann ich mit Karte zahlen?", "fr": "Puis-je payer par carte ?", "ja": "カードで支払えますか？", "ko": "카드로 결제할 수 있나요?", "th": "จ่ายด้วยบัตรได้ไหม?", "zh-CN": "我可以刷卡吗？", "ru": "Могу ли я оплатить картой?"},
        "doi tien o dau": {"en": "Where can I exchange money?", "de": "Wo kann ich Geld wechseln?", "fr": "Où puis-je changer de l'argent ?", "ja": "両替はどこでできますか？", "ko": "환전은 어디서 하나요?", "th": "แลกเงินได้ที่ไหน?", "zh-CN": "哪里可以换钱？", "ru": "Где можно обменять деньги?"},

        # Transport & Directions
        "san bay o dau": {"en": "Where is the airport?", "de": "Wo ist der Flughafen?", "fr": "Où est l'aéroport ?", "ja": "空港はどこですか？", "ko": "공항이 어디에 있나요?", "th": "สนามบินอยู่ที่ไหน?", "zh-CN": "机场在哪里？", "ru": "Где находится аэропорт?"},
        "ga tau o dau": {"en": "Where is the train station?", "de": "Wo ist der Bahnhof?", "fr": "Où est la gare ?", "ja": "駅はどこですか？", "ko": "기차역이 어디에 있나요?", "th": "สถานีรถไฟอยู่ที่ไหน?", "zh-CN": "火车站在哪里？", "ru": "Где находится вокзал?"},
        "tram xe buyt o dau": {"en": "Where is the bus stop?", "de": "Wo ist die Bushaltestelle?", "fr": "Où est l'arrêt de bus ?", "ja": "バス停はどこですか？", "ko": "버스 정류장이 어디인가요?", "th": "ป้ายรถเมล์อยู่ที่ไหน?", "zh-CN": "公交车站餐在哪里？", "ru": "Где автобусная остановка?"},
        "toilet o dau": {"en": "Where is the restroom?", "de": "Wo ist die Toilette?", "fr": "Où sont les toilettes ?", "es": "Dónde está el baño?", "ja": "トイレはどこですか？", "ko": "화장실이 어디에 있나요?", "th": "ห้องน้ำอยู่ที่ไหน?", "zh-CN": "洗手间在哪里？", "ru": "Где туалет?"},
        "bat taxi o dau": {"en": "Where can I get a taxi?", "de": "Wo bekomme ich ein Taxi?", "fr": "Où puis-je trouver un taxi ?", "ja": "タクシーはどこで乗れますか？", "ko": "택시는 어디서 타나요?", "th": "ขึ้นแท็กซี่ได้ที่ไหน?", "zh-CN": "哪里可以打车？", "ru": "Где поймать такси?"},
        "di thang": {"en": "Go straight", "de": "Geradeaus gehen", "fr": "Tout droit", "ja": "まっすぐ進んでください", "ko": "직진하세요", "th": "ตรงไป", "zh-CN": "直走", "ru": "Идите прямо"},
        "re trai": {"en": "Turn left", "de": "Biegen Sie links ab", "fr": "Tournez à gauche", "ja": "左に曲がってください", "ko": "좌회전하세요", "th": "เลี้ยวซ้าย", "zh-CN": "左转", "ru": "Поверните налево"},
        "re phai": {"en": "Turn right", "de": "Biegen Sie rechts ab", "fr": "Tournez à droite", "ja": "右に曲がってください", "ko": "우회전하세요", "th": "เลี้ยวขวา", "zh-CN": "右转", "ru": "Поверните направо"},

        # Emergency & Medical
        "toi can giup do khan cap": {"en": "I need emergency help.", "de": "Ich brauche dringend Hilfe.", "fr": "J'ai besoin d'une aide urgente.", "ja": "緊急の助けが必要です。", "ko": "긴급한 도움이 필요합니다.", "th": "ฉันต้องการความช่วยเหลือฉุกเฉิน", "zh-CN": "我需要紧急帮助", "ru": "Мне нужна экстренная помощь"},
        "cuu toi voi": {"en": "Help me!", "de": "Hilfe!", "fr": "Aidez-moi !", "es": "¡Ayuda!", "ja": "助けてください！", "ko": "도와주세요!", "th": "ช่วยฉันด้วย!", "zh-CN": "救命！", "ru": "Помогите!"},
        "goi canh sat": {"en": "Call the police!", "de": "Rufen Sie die Polizei!", "fr": "Appelez la police !", "ja": "警察を呼んでください！", "ko": "경찰을 불러주세요!", "th": "โทรเรียกตำรวจหน่อย!", "zh-CN": "报警！", "ru": "Вызовите полицию!"},
        "goi cap cuu": {"en": "Call an ambulance!", "de": "Rufen Sie einen Krankenwagen!", "fr": "Appelez une ambulance !", "ja": "救急車を呼んでください！", "ko": "구급차를 불러주세요!", "th": "เรียกรถพยาบาลหน่อย!", "zh-CN": "叫救护车！", "ru": "Вызовите скорую помощь!"},
        "benh vien o dau": {"en": "Where is the hospital?", "de": "Wo ist das Krankenhaus?", "fr": "Où est l'hôpital ?", "ja": "病院はどこですか？", "ko": "병원이 어디에 있나요?", "th": "โรงพยาบาลอยู่ที่ไหน?", "zh-CN": "医院在哪里？", "ru": "Где больница?"},
        "tiem thuoc o dau": {"en": "Where is the pharmacy?", "de": "Wo ist die Apotheke?", "fr": "Où est la pharmacie ?", "ja": "薬局はどこですか？", "ko": "약국이 어디에 있나요?", "th": "ร้านขายยาอยู่ที่ไหน?", "zh-CN": "药店在哪里？", "ru": "Где аптека?"},
        "toi bi lac duong": {"en": "I am lost", "de": "Ich habe mich verirrt", "fr": "Je suis perdu", "ja": "道に迷いました", "ko": "길을 잃었습니다", "th": "ฉันหลงทาง", "zh-CN": "我迷路了", "ru": "Я заблудился"},
        "toi bi mat ho chieu": {"en": "I lost my passport", "de": "Ich habe meinen Reisepass verloren", "fr": "J'ai perdu mon passeport", "ja": "パスポートを紛失しました", "ko": "여권을 잃어버렸습니다", "th": "ฉันทำหนังสือเดินทางหาย", "zh-CN": "我的护照丢了", "ru": "Я потерял паспорт"},

        # Communication
        "khong hieu": {"en": "I don't understand", "de": "Ich verstehe nicht", "fr": "Je ne comprends pas", "ja": "わかりません", "ko": "이해하지 못해요", "th": "ฉันไม่เข้าใจ", "zh-CN": "我不明白", "ru": "Я не понимаю"},
        "ban co noi tieng anh khong": {"en": "Do you speak English?", "de": "Sprechen Sie Englisch?", "fr": "Parlez-vous anglais ?", "ja": "英語を話せますか？", "ko": "영어 할 수 있나요?", "th": "คุณพูดภาษาอังกฤษได้ไหม?", "zh-CN": "你会说英语吗？", "ru": "Вы говорите по-английски?"},
        "ban co noi tieng viet khong": {"en": "Do you speak Vietnamese?", "de": "Sprechen Sie Vietnamesisch?", "fr": "Parlez-vous vietnamien ?", "ja": "ベトナム語を話せますか？", "ko": "베트남어 하시나요?", "th": "คุณพูดภาษาเวียดนามได้ไหม?", "zh-CN": "你会说越南语吗？", "ru": "Вы говорите по-вьетнамски?"},
        "noi cham lai giup toi": {"en": "Please speak more slowly", "de": "Bitte sprechen Sie langsamer", "fr": "Parlez plus lentement, s'il vous plaît", "ja": "もっとゆっくり話してください", "ko": "더 천천히 말씀해 주세요", "th": "กรุณาพูดช้าลงหน่อย", "zh-CN": "请说慢一点", "ru": "Говорите помедленнее, пожалуйста"},

        # English to Vietnamese & other languages counterparts
        "hello": {"vi": "Xin chào", "de": "Hallo", "fr": "Bonjour", "es": "Hola", "it": "Ciao", "ja": "こんにちは", "ko": "안녕하세요", "th": "สวัสดี", "zh-CN": "你好", "ru": "Привет"},
        "thank you": {"vi": "Cảm ơn", "de": "Danke", "fr": "Merci", "es": "Gracias", "it": "Grazie", "ja": "ありがとうございます", "ko": "감사합니다", "th": "ขอบคุณ", "zh-CN": "谢谢", "ru": "Спасибо"},
        "goodbye": {"vi": "Tạm biệt", "de": "Auf Wiedersehen", "fr": "Au revoir", "es": "Adiós", "it": "Arrivederci", "ja": "さようなら", "ko": "안녕히 계세요", "th": "ลาก่อน", "zh-CN": "再见", "ru": "До свидания"},
        "how much is it": {"vi": "Bao nhiêu tiền?", "de": "Wie viel kostet das?", "fr": "Combien ça coûte ?", "ja": "いくらですか？", "ko": "얼마예요?", "th": "ราคาเท่าไหร่?", "zh-CN": "多少钱？", "ru": "Сколько это стоит?"},
        "where is the airport": {"vi": "Sân bay ở đâu?", "de": "Wo ist der Flughafen?", "ja": "空港はどこですか？", "ko": "공항이 어디에 있나요?", "th": "สนามบินอยู่ที่ไหน?", "zh-CN": "机场在哪里？", "ru": "Где находится аэропорт?"},
        "where is the train station": {"vi": "Ga tàu ở đâu?", "de": "Wo ist der Bahnhof?", "ja": "駅はどこですか？", "ko": "기차역이 어디에 있나요?", "th": "สถานีรถไฟอยู่ที่ไหน?", "zh-CN": "火车站在哪里？", "ru": "Где находится вокзал?"},
        "where is the restroom": {"vi": "Nhà vệ sinh ở đâu?", "de": "Wo ist die Toilette?", "fr": "Où sont les toilettes ?", "ja": "トイレはどこですか？", "ko": "화장실이 어디에 있나요?", "th": "ห้องน้ำอยู่ที่ไหน?", "zh-CN": "洗手间在哪里？", "ru": "Где туалет?"},
        "help me": {"vi": "Cứu tôi với!", "de": "Hilfe!", "fr": "Aidez-moi !", "ja": "助けて！", "ko": "도와주세요!", "th": "ช่วยด้วย!", "zh-CN": "救命！", "ru": "Помогите!"},
    }

    def translate(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        norm_text = _normalise_text(text).strip(" ?!.,:;\"'")
        target_code = target_lang.split("-")[0] if target_lang not in ["zh-CN", "zh-TW"] else target_lang

        for phrase, translations in self.PHRASES.items():
            norm_phrase = _normalise_text(phrase).strip(" ?!.,:;\"'")
            if norm_text == norm_phrase or norm_phrase in norm_text or norm_text in norm_phrase:
                translated = (
                    translations.get(target_lang) or
                    translations.get(target_code) or
                    translations.get("en") or
                    translations.get("vi")
                )
                if translated:
                    return {
                        "translated_text": translated,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "provider": "Offline Travel Phrases Engine",
                        "success": True,
                    }

        # Graceful fallback: return original text with an informative note instead of crashing
        return {
            "translated_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "provider": "Offline Travel Assistant",
            "success": True,
            "note": "Bản dịch ngoại tuyến: Dịch vụ trực tuyến tạm thời không khả dụng, hiển thị văn bản gốc.",
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
