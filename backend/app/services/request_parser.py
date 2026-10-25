"""Deterministic parsing and validation for travel-planning prompts.

Extracts origin, destination, duration, budget, travelers, preferences, and intent
with precise differentiation between travel origin (where user departs from)
and travel destination (where user wants to visit).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, Optional, Tuple


def _normalise(value: str) -> str:
    """Case-fold text while retaining a predictable representation of Vietnamese without marks."""
    decomposed = unicodedata.normalize("NFD", value.casefold())
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return without_marks.replace("đ", "d")


# Specific Cities, Villages, and Landmarks (checked first)
SPECIFIC_DESTINATIONS: tuple[tuple[tuple[str, ...], str], ...] = (
    # Japan
    (("kyoto",), "Kyoto, Nhật Bản"),
    (("osaka",), "Osaka, Nhật Bản"),
    (("tokyo",), "Tokyo, Nhật Bản"),
    (("shirakawa", "shirakawago"), "Shirakawa-go, Gifu, Nhật Bản"),
    (("nara",), "Nara, Nhật Bản"),
    (("sapporo", "hokkaido"), "Sapporo, Hokkaido, Nhật Bản"),
    (("fukuoka",), "Fukuoka, Nhật Bản"),
    (("hiroshima",), "Hiroshima, Nhật Bản"),
    # South Korea
    (("busan",), "Busan, Hàn Quốc"),
    (("jeju",), "Đảo Jeju, Hàn Quốc"),
    (("incheon",), "Incheon, Hàn Quốc"),
    (("seoul",), "Seoul, Hàn Quốc"),
    (("nami",), "Đảo Nami, Hàn Quốc"),
    # Vietnam
    (("sa pa", "sapa", "cat cat", "fansipan"), "Bản Cát Cát, Sa Pa, Việt Nam"),
    (("da nang", "ba na"), "Đà Nẵng, Việt Nam"),
    (("hoi an",), "Hội An, Quảng Nam, Việt Nam"),
    (("hue",), "Huế, Việt Nam"),
    (("da lat",), "Đà Lạt, Lâm Đồng, Việt Nam"),
    (("nha trang",), "Nha Trang, Khánh Hòa, Việt Nam"),
    (("phu quoc",), "Phú Quốc, Kiên Giang, Việt Nam"),
    (("ha long", "vinh ha long"), "Vịnh Hạ Long, Quảng Ninh, Việt Nam"),
    (("ninh binh", "trang an"), "Ninh Bình, Việt Nam"),
    (("quy nhon",), "Quy Nhơn, Bình Định, Việt Nam"),
    (("vung tau",), "Vũng Tàu, Việt Nam"),
    (("ha noi",), "Hà Nội, Việt Nam"),
    (("ho chi minh", "sai gon", "saigon", "tphcm"), "TP. Hồ Chí Minh, Việt Nam"),
    # Europe
    (("hallstatt", "halstatt"), "Hallstatt, Áo"),
    (("vienna",), "Vienna, Áo"),
    (("salzburg",), "Salzburg, Áo"),
    (("zermatt", "matterhorn"), "Zermatt, Thụy Sĩ"),
    (("zurich",), "Zurich, Thụy Sĩ"),
    (("geneva", "geneve"), "Geneva, Thụy Sĩ"),
    (("lucerne", "luzern"), "Lucerne, Thụy Sĩ"),
    (("interlaken", "jungfrau"), "Interlaken, Thụy Sĩ"),
    (("grindelwald",), "Grindelwald, Thụy Sĩ"),
    (("paris",), "Paris, Pháp"),
    (("nice",), "Nice, Pháp"),
    (("lyon",), "Lyon, Pháp"),
    (("rome", "roma"), "Rome, Ý"),
    (("venice", "venezia"), "Venice, Ý"),
    (("florence", "firenze"), "Florence, Ý"),
    (("milan", "milano"), "Milan, Ý"),
    (("positano", "amalfi"), "Positano, Ý"),
    (("london",), "London, Vương Quốc Anh"),
    (("liverpool",), "Liverpool, Vương Quốc Anh"),
    (("manchester",), "Manchester, Vương Quốc Anh"),
    (("birmingham",), "Birmingham, Vương Quốc Anh"),
    (("edinburgh",), "Edinburgh, Scotland"),
    (("berlin",), "Berlin, Đức"),
    (("munich", "munchen"), "Munich, Đức"),
    (("frankfurt",), "Frankfurt, Đức"),
    (("amsterdam",), "Amsterdam, Hà Lan"),
    (("giethoorn",), "Giethoorn, Hà Lan"),
    (("santorini", "oia"), "Santorini, Hy Lạp"),
    (("reykjavik",), "Reykjavik, Iceland"),
    (("reine", "lofoten"), "Reine, Na Uy"),
    (("oslo",), "Oslo, Na Uy"),
    # Southeast Asia & Others
    (("bangkok",), "Bangkok, Thái Lan"),
    (("chiang mai",), "Chiang Mai, Thái Lan"),
    (("phuket",), "Phuket, Thái Lan"),
    (("singapore",), "Singapore"),
    (("bali",), "Đảo Bali, Indonesia"),
    (("kuala lumpur",), "Kuala Lumpur, Malaysia"),
    (("bac kinh", "beijing"), "Bắc Kinh, Trung Quốc"),
    (("thuong hai", "shanghai"), "Thượng Hải, Trung Quốc"),
    (("truong gia gioi",), "Trương Gia Giới, Trung Quốc"),
    (("phuong hoang co tran",), "Phượng Hoàng Cổ Trấn, Trung Quốc"),
    (("dai bac", "taipei"), "Đài Bắc, Đài Loan"),
    (("sydney",), "Sydney, Úc"),
    (("melbourne",), "Melbourne, Úc"),
    (("new york", "nyc"), "New York, Mỹ"),
    (("chicago",), "Chicago, Mỹ"),
    (("boston",), "Boston, Mỹ"),
    (("washington", "washington dc"), "Washington D.C., Mỹ"),
    (("san francisco",), "San Francisco, Mỹ"),
    (("los angeles",), "Los Angeles, Mỹ"),
    (("hawaii", "honolulu"), "Hawaii, Mỹ"),
)

# Broad Country Level (checked when no specific city was mentioned)
COUNTRY_DESTINATIONS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("khap nhat ban", "di khap nhat ban", "kham pha khap nhat ban", "nhat ban", "japan", "nippon"), "Tokyo, Nhật Bản"),
    (("khap han quoc", "di khap han quoc", "kham pha khap han quoc", "han quoc", "south korea", "korea"), "Seoul, Hàn Quốc"),
    (("khap thuy si", "di khap thuy si", "kham pha khap thuy si", "thuy si", "switzerland"), "Zermatt, Thụy Sĩ"),
    (("khap nuoc ao", "di khap nuoc ao", "kham pha khap nuoc ao", "nuoc ao", "austria"), "Vienna, Áo"),
    (("khap nuoc phap", "di khap nuoc phap", "kham pha khap nuoc phap", "nuoc phap", "france"), "Paris, Pháp"),
    (("khap nuoc y", "di khap nuoc y", "kham pha khap nuoc y", "nuoc y", "italy"), "Rome, Ý"),
    (("khap thai lan", "di khap thai lan", "kham pha khap thai lan", "thai lan", "thailand"), "Bangkok, Thái Lan"),
    (("khap nuoc anh", "di khap nuoc anh", "kham pha khap nuoc anh", "nuoc anh", "vuong quoc anh", "united kingdom", "uk", "england"), "London, Vương Quốc Anh"),
    (("khap nuoc duc", "di khap nuoc duc", "kham pha khap nuoc duc", "nuoc duc", "germany"), "Berlin, Đức"),
    (("khap nuoc my", "di khap nuoc my", "kham pha khap nuoc my", "nuoc my", "hoa ky", "usa", "united states"), "New York, Mỹ"),
    (("khap nuoc uc", "di khap nuoc uc", "kham pha khap nuoc uc", "nuoc uc", "australia"), "Sydney, Úc"),
    (("trung quoc", "china", "khap trung quoc"), "Bắc Kinh, Trung Quốc"),
    (("dai loan", "taiwan", "khap dai loan"), "Đài Bắc, Đài Loan"),
    (("ha lan", "netherlands", "khap ha lan"), "Amsterdam, Hà Lan"),
    (("hy lap", "greece", "khap hy lap"), "Santorini, Hy Lạp"),
    (("na uy", "norway", "khap na uy"), "Oslo, Na Uy"),
    (("viet nam", "vietnam", "khap viet nam"), "Đà Nẵng, Việt Nam"),
)

KNOWN_ORIGINS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("ho chi minh", "sai gon", "saigon", "tphcm", "tp hcm", "tp.hcm", "thanh pho ho chi minh"), "TP. Hồ Chí Minh, Việt Nam"),
    (("ha noi", "hanoi", "thanh pho ha noi"), "Hà Nội, Việt Nam"),
    (("da nang", "danang", "thanh pho da nang"), "Đà Nẵng, Việt Nam"),
    (("can tho", "thanh pho can tho"), "Cần Thơ, Việt Nam"),
    (("hai phong", "thanh pho hai phong"), "Hải Phòng, Việt Nam"),
    (("nha trang",), "Nha Trang, Việt Nam"),
    (("hue",), "Huế, Việt Nam"),
    (("da lat",), "Đà Lạt, Việt Nam"),
)

CURRENCY_TO_VND = {
    "VND": 1.0,
    "USD": 25_450.0,
    "EUR": 27_650.0,
    "GBP": 34_336.64,
    "CHF": 29_500.0,
    "JPY": 167.0,
    "KRW": 18.4,
    "THB": 697.0,
    "SGD": 18_850.0,
    "AUD": 16_600.0,
    "CAD": 18_400.0,
}


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match complete words, avoiding false hits such as 'ao' in 'bao'."""
    return bool(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text))


def _extract_origin(text: str, normalised: str) -> Tuple[str, str]:
    """
    Extracts origin of traveler, e.g. 'Chúng tôi ở Thành Phố Hồ Chí Minh',
    'khởi hành từ Hà Nội', 'từ Tp.HCM đến Liverpool'.
    Returns (origin_name, origin_clause_text).
    """
    # Clean text to normalize dots like tp.hcm -> tp hcm
    clean_norm = re.sub(r"[.,]", " ", normalised)
    clean_norm = re.sub(r"\s+", " ", clean_norm).strip()

    # 1. Match origin expressions
    origin_patterns = (
        r"(?:chung toi o|chung em o|toi o|minh o|nha o|song tai|song o|o|tai)\s+(?:thanh pho|tp\.?|tinh)?\s*([a-z\s]+?)(?=[.,;!?]|$)",
        r"(?:khoi hanh tu|xuat phat tu|bay tu|di tu|tu)\s+(?:thanh pho|tp\.?|tinh)?\s*([a-z\s]+?)(?=[.,;!?]|$|\s+(?:den|di|toi))",
    )
    for pattern in origin_patterns:
        match = re.search(pattern, clean_norm, re.IGNORECASE)
        if match:
            matched_place = match.group(1).strip()
            for keywords, canonical in KNOWN_ORIGINS:
                if any(kw in matched_place for kw in keywords):
                    return canonical, match.group(0)

    # 2. Direct origin check if specified with 'o [city]' or 'tu [city]'
    for keywords, canonical in KNOWN_ORIGINS:
        for kw in keywords:
            if re.search(rf"\b(?:o|tai|tu|song o)\s+(?:thanh pho|tp\.?|tinh\s+)?{re.escape(kw)}\b", clean_norm):
                return canonical, kw

    # 3. Check combined raw and normalized text for origin keywords
    combined_raw = f"{text} {normalised}".lower()
    if re.search(r"\b(?:o|tu|tai)\s+(?:thanh pho\s+|tp\.?\s*)?(?:ho chi minh|sai gon|tphcm|tp hcm)\b", combined_raw) or "chung toi o thanh pho ho chi minh" in combined_raw:
        return "TP. Hồ Chí Minh, Việt Nam", "ho chi minh"
    if re.search(r"\b(?:o|tu|tai)\s+(?:thanh pho\s+|tp\.?\s*)?(?:ha noi|hanoi)\b", combined_raw):
        return "Hà Nội, Việt Nam", "ha noi"
    if re.search(r"\b(?:o|tu|tai)\s+(?:thanh pho\s+|tp\.?\s*)?(?:da nang|danang)\b", combined_raw):
        return "Đà Nẵng, Việt Nam", "da nang"

    return "Hà Nội, Việt Nam", ""


def _extract_destination(original: str, normalised: str, origin_clause: str = "") -> Optional[str]:
    """
    Extracts destination while explicitly ignoring the origin clause.
    """
    # Remove origin clause from text so that "Chúng tôi ở TP. Hồ Chí Minh" does not trigger Ho Chi Minh
    clean_norm = normalised
    if origin_clause:
        clean_norm = clean_norm.replace(origin_clause, " ")

    # 1. FIRST: Check for "khắp" country phrases (highest priority)
    for keywords, canonical in COUNTRY_DESTINATIONS:
        if any(_contains_phrase(clean_norm, kw) for kw in keywords):
            return canonical

    # 2. Look specifically for travel/destination action phrases
    dest_action_match = re.search(
        r"(?:di khap|kham pha khap|du lich khap|di|den|toi|tham|kham pha|du lich|nghi duong|check-in|tour|chuyen di|travel to|visit|go to|explore)\s+"
        r"(?:dat nuoc|nuoc|quoc gia|thanh pho|lang|dao|thi tran|ban)?\s*"
        r"([a-z0-9\s,.'-]{2,60}?)"
        r"(?=\s*(?:\d+\s*(?:ngay|dem|day|night)|trong|vao|thang|ngan sach|budget|bao gom|danh cho|chung toi|gia dinh|tu|voi|cho|$))",
        clean_norm,
        re.IGNORECASE
    )
    if dest_action_match:
        target_phrase = dest_action_match.group(1).strip()
        # Check specific spots first
        for keywords, canonical in SPECIFIC_DESTINATIONS:
            if any(_contains_phrase(target_phrase, kw) for kw in keywords):
                return canonical
        # Check country defaults again (in case missed in step 1)
        for keywords, canonical in COUNTRY_DESTINATIONS:
            if any(_contains_phrase(target_phrase, kw) for kw in keywords):
                return canonical

    # 3. Check full text (minus origin clause) for specific destinations
    for keywords, canonical in SPECIFIC_DESTINATIONS:
        if any(_contains_phrase(clean_norm, kw) for kw in keywords):
            return canonical

    # 4. Fallback travel verb regex
    if dest_action_match:
        candidate = re.sub(r"\s+", " ", dest_action_match.group(1)).strip(" ,.-")
        if len(candidate) >= 2 and candidate not in {"do", "day", "nay", "khap"}:
            return candidate.title()

    return None


def _extract_dates_and_duration(text: str, original: str) -> Tuple[int, str, str]:
    """
    Extracts duration in days and precise start_date and end_date.
    Properly handles date ranges like '25-7 đến 5-8' (12 days) or '25/07 - 05/08'.
    """
    from datetime import datetime, timedelta

    combined = f"{text} {original.lower()}"
    current_year = 2026

    # 1. Date range pattern: dd-mm (or dd/mm) đến dd-mm (or dd/mm)
    date_range_match = re.search(
        r"(?:tu\s+)?(?:ngay\s+)?(\d{1,2})[-/](\d{1,2})(?:[-/](\d{4}))?\s*(?:den|đến|to|-|–)\s*(?:ngay\s+)?(\d{1,2})[-/](\d{1,2})(?:[-/](\d{4}))?",
        combined,
        re.IGNORECASE
    )
    if date_range_match:
        try:
            start_day = int(date_range_match.group(1))
            start_month = int(date_range_match.group(2))
            start_year = int(date_range_match.group(3)) if date_range_match.group(3) else current_year

            end_day = int(date_range_match.group(4))
            end_month = int(date_range_match.group(5))
            end_year = int(date_range_match.group(6)) if date_range_match.group(6) else start_year

            start_date = datetime(start_year, start_month, start_day)
            end_date = datetime(end_year, end_month, end_day)

            if end_date < start_date:
                end_date = datetime(start_year + 1, end_month, end_day)

            duration = (end_date - start_date).days + 1
            if 1 <= duration <= 60:
                return duration, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        except Exception:
            pass

    # 2. Vietnamese phrase range: từ ngày d tháng m đến ngày d tháng m
    vn_text_range = re.search(
        r"(?:tu\s+)?(?:ngay\s+)?(\d{1,2})\s+(?:thang|tháng)\s+(\d{1,2})\s*(?:den|đến|to|-)\s*(?:ngay\s+)?(\d{1,2})\s+(?:thang|tháng)\s+(\d{1,2})",
        combined,
        re.IGNORECASE
    )
    if vn_text_range:
        try:
            start_day = int(vn_text_range.group(1))
            start_month = int(vn_text_range.group(2))
            end_day = int(vn_text_range.group(3))
            end_month = int(vn_text_range.group(4))

            start_date = datetime(current_year, start_month, start_day)
            end_date = datetime(current_year, end_month, end_day)
            if end_date < start_date:
                end_date = datetime(current_year + 1, end_month, end_day)
            duration = (end_date - start_date).days + 1
            if 1 <= duration <= 60:
                return duration, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        except Exception:
            pass

    # 3. Explicit duration in days: "7 ngày 6 đêm", "5 ngày", "4n3d", etc.
    duration = 4
    match = re.search(r"\b(\d{1,2})\s*(?:ngay|days?|n)\b", text, re.IGNORECASE)
    if match:
        duration = max(1, min(int(match.group(1)), 30))
    else:
        compact = re.search(r"\b(\d{1,2})n\s*\d{1,2}d\b", text, re.IGNORECASE)
        if compact:
            duration = max(1, min(int(compact.group(1)), 30))

    # 4. Check for travel month: "tháng 12", "tháng 7", etc.
    month_match = re.search(r"(?:thang|tháng|month)\s*(1[0-2]|[1-9])\b", combined, re.IGNORECASE)
    if month_match:
        travel_month = int(month_match.group(1))
        start_date = datetime(current_year, travel_month, 1)
        end_date = start_date + timedelta(days=duration - 1)
        return duration, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # 5. Default fallback: 30 days from now
    base_date = datetime.now() + timedelta(days=30)
    start_date_str = base_date.strftime("%Y-%m-%d")
    end_date_str = (base_date + timedelta(days=duration - 1)).strftime("%Y-%m-%d")
    return duration, start_date_str, end_date_str


def _extract_travelers(text: str) -> int:
    match = re.search(r"\b(\d{1,2})\s*(?:nguoi|khach|thanh vien|pax|people|persons?|ve)\b", text, re.IGNORECASE)
    if match:
        return max(1, min(int(match.group(1)), 20))
    if any(term in text for term in ("gia dinh 4", "4 nguoi")):
        return 4
    if any(term in text for term in ("gia dinh", "family")):
        return 4
    if any(term in text for term in ("mot minh", "solo", "doc than")):
        return 1
    return 2


def _extract_budget(text: str, original: str, travelers: int) -> tuple[float, str]:
    combined = f"{text} {original}".lower()

    # 1. Bảng Anh (GBP) - e.g. "10000 bảng anh", "10,000 bảng", "10000 gbp", "£10000"
    gbp_match = re.search(r"(?:£|gbp)?\s*(\d+(?:[.,]\d+)?)\s*(?:bảng\s*anh|bang\s*anh|bảng|bang|gbp|pounds?|£)\b", combined, re.IGNORECASE)
    if not gbp_match:
        gbp_match = re.search(r"£\s*(\d+(?:[.,]\d+)?)", combined)
    if gbp_match:
        amount = float(gbp_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["GBP"], "GBP"

    # 2. Triệu / Tr / Củ (VND millions) - e.g. "500 triệu", "500tr", "500 củ", "30 triệu"
    trieu_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:trieu|triệu|tr|cu|củ|million|m)\b", combined, re.IGNORECASE)
    if trieu_match:
        return float(trieu_match.group(1).replace(",", ".")) * 1_000_000, "VND"

    # 3. Explicit VND amount with dot/comma formatting: "50.000.000 VND", "30,000,000 đ"
    vnd_match = re.search(r"(?:vnd|vnđ|dong|đồng|đ)?\s*(\d{1,3}(?:[.,]\d{3})+)\s*(?:vnd|vnđ|dong|đồng|đ)?", combined, re.IGNORECASE)
    if vnd_match:
        return float(re.sub(r"[.,]", "", vnd_match.group(1))), "VND"

    # 4. USD / Đô la - e.g. "5000 usd", "$5000", "5000 đô", "5000 đô la"
    usd_match = re.search(r"(?:\$)?\s*(\d+(?:[.,]\d+)?)\s*(?:usd|đô\s*la|do\s*la|đô|do|dollars?|\$)\b", combined, re.IGNORECASE)
    if not usd_match:
        usd_match = re.search(r"\$\s*(\d+(?:[.,]\d+)?)", combined)
    if usd_match:
        amount = float(usd_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["USD"], "USD"

    # 5. EUR / Euro - e.g. "3000 eur", "3000 euro", "€3000"
    eur_match = re.search(r"(?:€)?\s*(\d+(?:[.,]\d+)?)\s*(?:eur|euro|€)\b", combined, re.IGNORECASE)
    if not eur_match:
        eur_match = re.search(r"€\s*(\d+(?:[.,]\d+)?)", combined)
    if eur_match:
        amount = float(eur_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["EUR"], "EUR"

    # 6. JPY / Yên - e.g. "100 man yên", "500000 yên", "500000 jpy", "¥500000"
    man_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:man\s*yên|man\s*yen|man)\b", combined, re.IGNORECASE)
    if man_match:
        amount = float(man_match.group(1).replace(",", ".")) * 10_000
        return amount * CURRENCY_TO_VND["JPY"], "JPY"
    jpy_match = re.search(r"(?:¥)?\s*(\d+(?:[.,]\d+)?)\s*(?:jpy|yên|yen|¥)\b", combined, re.IGNORECASE)
    if jpy_match:
        amount = float(jpy_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["JPY"], "JPY"

    # 7. KRW / Won - e.g. "2000000 won", "2000000 krw", "₩2000000"
    krw_match = re.search(r"(?:₩)?\s*(\d+(?:[.,]\d+)?)\s*(?:krw|won|₩)\b", combined, re.IGNORECASE)
    if krw_match:
        amount = float(krw_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["KRW"], "KRW"

    # 8. THB / Baht - e.g. "50000 baht", "50000 thb"
    thb_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:thb|baht|bạt)\b", combined, re.IGNORECASE)
    if thb_match:
        amount = float(thb_match.group(1).replace(",", "."))
        return amount * CURRENCY_TO_VND["THB"], "THB"

    # 9. Other currencies (AUD, CAD, SGD, CHF)
    other_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(aud|cad|sgd|chf)\b", combined, re.IGNORECASE)
    if other_match:
        amount = float(other_match.group(1).replace(",", "."))
        curr = other_match.group(2).upper()
        return amount * CURRENCY_TO_VND.get(curr, 25_000.0), curr

    return 25_000_000 * (travelers / 2), "VND"


def _extract_preferences(text: str) -> list[str]:
    rules = {
        "food": ("am thuc", "an uong", "nha hang", "mon ngon", "food", "cuisine", "an vat"),
        "culture": ("van hoa", "lich su", "bao tang", "chua", "cung dien", "heritage", "culture", "co kinh"),
        "nature": ("thien nhien", "ngam canh", "nui", "ho", "rung", "nature", "landscape", "tuyet", "hoa anh dao"),
        "shopping": ("mua sam", "shopping", "mall", "cho dem", "pho di bo"),
        "relaxation": ("nghi duong", "thu gian", "resort", "spa", "relax", "tam bien"),
        "adventure": ("trek", "leo nui", "truot tuyet", "adventure", "hiking", "mao hiem"),
    }
    preferences = [name for name, terms in rules.items() if any(_contains_phrase(text, term) for term in terms)]
    return preferences or ["culture", "food", "nature"]


def parse_travel_request(prompt: str) -> Dict[str, Any]:
    text = prompt.strip()
    normalised = _normalise(text)

    # 1. Extract Origin first
    origin, origin_clause = _extract_origin(text, normalised)

    # 2. Extract Destination (excluding origin clause)
    destination = _extract_destination(text, normalised, origin_clause)

    # 3. Extract Travelers & Duration & Dates & Budget
    travelers = _extract_travelers(normalised)
    duration, start_date, end_date = _extract_dates_and_duration(normalised, text)
    budget_vnd, budget_currency = _extract_budget(normalised, text, travelers)
    month_match = re.search(r"(?:thang|month)\s*(1[0-2]|[1-9])\b", normalised)

    missing_fields = [] if destination else ["destination"]
    return {
        "destination": destination or "Tokyo, Nhật Bản",
        "duration": duration,
        "start_date": start_date,
        "end_date": end_date,
        "budget": round(budget_vnd, 2),
        "currency": "VND",
        "input_budget_currency": budget_currency,
        "preferences": _extract_preferences(normalised),
        "travel_month": int(month_match.group(1)) if month_match else int(start_date.split("-")[1]),
        "origin": origin,
        "travelers": travelers,
        "missing_fields": missing_fields,
        "confidence": "high" if destination else "needs_clarification",
    }


def classify_intent(prompt: str) -> str:
    text = _normalise(prompt)
    replan_terms = ("thay doi", "doi gio", "doi ngay", "doi lich", "huy tour", "huy phong", "huy ve", "huy lich trinh", "replan", "adjust itinerary")
    if any(_contains_phrase(text, term) for term in replan_terms) or _contains_phrase(text, "huy"):
        return "REPLAN_TRIP"
    support_terms = ("dang o", "nhac lich", "gan day", "thoi tiet", "near me", "quan an", "quan ngon", "an uong")
    if any(_contains_phrase(text, term) for term in support_terms):
        return "IN_TRIP_SUPPORT"
    return "PLAN_NEW_TRIP"
