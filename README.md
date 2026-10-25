# 🌍 UNIVERSAL AI TRAVEL AGENT PLATFORM 2.0
### Hệ Thống Trợ Lý Du Lịch Thông Minh Đa Tác Nhân (Multi-Agent) Hỗ Trợ Toàn Cầu

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent%20DAG-orange)](https://langchain-ai.github.io/langgraph/)
[![Next.js](https://img.shields.io/badge/Next.js-16.3%20Turbopack-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![React Native](https://img.shields.io/badge/React%20Native-Expo%20SDK%2057-000020?logo=expo&logoColor=white)](https://expo.dev/)
[![SQLite / PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pytest](https://img.shields.io/badge/Pytest-19%2F19%20Passed-brightgreen?logo=pytest&logoColor=white)](https://pytest.org/)

---

## 📖 GIỚI THIỆU TỔNG QUAN (OVERVIEW)

**Universal AI Travel Agent Platform** là nền tảng công nghệ du lịch thông minh thế hệ mới, ứng dụng kiến trúc **Đa tác nhân (Multi-Agent System)** xây dựng trên **LangGraph** và **FastAPI**. 

Hệ thống cho phép người dùng lập kế hoạch du lịch hoàn chỉnh bằng ngôn ngữ tự nhiên cho **bất kỳ quốc gia, thành phố, thị trấn hay làng mạc nào trên toàn thế giới** theo thời gian thực (Real-time Worldwide Coverage) mà không bị giới hạn bởi dữ liệu gán cứng (hardcoded data).

### Triết Lý Thiết Kế Cốt Lõi:
1. **Phạm Vi Toàn Cầu Thực Sự (Universal Worldwide Coverage)**: Tích hợp dịch vụ định vị địa lý OpenStreetMap Nominatim, cơ sở dữ liệu sân bay IATA quốc tế và bộ tính toán tọa độ mặt cầu Haversine, hỗ trợ từ các đô thị sầm uất (Tokyo, Paris, New York) đến các ngôi làng di sản thanh bình (Hallstatt, Giethoorn, Zermatt, Cát Cát).
2. **Kiến Trúc Multi-Agent Độc Lập & Xác Thực Chặt Chẽ**: Phân tách trách nhiệm thành 15 Node chuyên biệt: phân tích nhu cầu, tra cứu địa lý, điều tiết ngân sách, tìm kiếm chuyến bay/khách sạn/ẩm thực, sắp xếp thời gian biểu, tối ưu khoảng cách và thẩm định lịch trình.
3. **Cơ Chế Re-planning Động & Quản Lý Phiên Bản (Trip Versioning)**: Khi người dùng sửa đổi bất kỳ hoạt động nào, hệ thống tự động tính toán lại các phụ thuộc thời gian, dịch chuyển các mốc check-in, ăn uống, di chuyển và lưu trữ lịch sử phiên bản (`TripVersion`) vào cơ sở dữ liệu để xem lại hoặc khôi phục bất cứ lúc nào.
4. **Human-in-the-Loop & Utilities Hub**: Đề xuất dịch vụ (vé máy bay, khách sạn, tour) ở trạng thái chờ duyệt (`PENDING`), trao quyền chủ động cho người dùng xác nhận hoặc hủy bỏ trước khi quyết định.
5. **Đồng Bộ Đa Nền Tảng (Web Next.js 16 & Mobile Expo SDK 57)**: Đồng bộ liền mạch dữ liệu tour, công cụ đổi ngoại tệ trực tiếp, dịch thuật du lịch offline an toàn và trợ lý ảo giải đáp thông tin dọc đường đi (In-Trip Assistant).

---

## 🏛️ KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống vận hành theo quy trình xử lý đồ thị có hướng không chu trình (**DAG**) của LangGraph:

```mermaid
flowchart TD
    User([Khách Hàng Nhập Yêu Cầu]) --> N1[1. User Request Analyzer]
    N1 --> N2[2. Requirement Extractor<br/>OpenAI GPT-4o / Hybrid Deterministic Parser]
    
    N2 -->|Thiếu Điểm Đến| N3[3. Clarification Node<br/>Gợi ý Điểm Đến Phổ Biến]
    N3 --> EndClar([Phản Hồi & Chờ Người Dùng Chọn])
    
    N2 -->|Đầy Đủ Điểm Đến| N4[4. Destination Analyzer<br/>Nominatim Geocoding & IATA Discovery]
    N4 --> N5[5. Budget Analyzer<br/>Phân Bổ Định Mức Chi Tiêu]
    N5 --> N6[6. Search Planner]
    
    N6 --> N7[7. Flight Search]
    N7 --> N8[8. Hotel Search]
    N8 --> N9[9. Activity Search]
    N9 --> N10[10. Restaurant Search]
    
    N10 --> N11[11. Itinerary Generator<br/>Tạo Lịch Trình Chi Tiết Theo Chủ Đề]
    N11 --> N12[12. Distance Optimizer<br/>Haversine Distance & Khung Giờ Tuyến Tính]
    N12 --> N13[13. Budget Validator<br/>Kiểm Định Ngân Sách Thực Tế]
    N13 --> N14[14. Schedule Validator<br/>Loại Bỏ Xung Đột Thời Gian]
    N14 --> N15[15. Final Itinerary & DB Persistence<br/>Lưu Trip, ItineraryDay, Items, Version 1]
    
    N15 --> Output([Giao Diện Web Next.js 16 & Mobile Expo SDK 57])
```

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT STRUCTURE)

```
Travel_Agent/
├── backend/                       # Backend FastAPI + LangGraph AI Core
│   ├── app/
│   │   ├── agent/                 # Kiến trúc Multi-Agent LangGraph
│   │   │   ├── tools/             # Bộ cung cấp dịch vụ (Universal Providers)
│   │   │   │   ├── base.py        # Abstract Base Interfaces
│   │   │   │   ├── registry.py    # Tool Registry trung tâm
│   │   │   │   └── universal_provider.py # Tra cứu toàn cầu (Flights, Hotels, Dining, Activities)
│   │   │   ├── graph.py           # Định nghĩa StateGraph & các Conditional Edges
│   │   │   ├── nodes.py           # 15 Agent Processing Nodes chuyên sâu
│   │   │   └── state.py           # Định nghĩa TravelAgentState kiểu dữ liệu TypedDict
│   │   ├── api/                   # RESTful API Endpoints
│   │   │   ├── agent.py           # /agent/plan-trip, /agent/replan, /agent/in-trip-support
│   │   │   ├── auth.py            # Xác thực người dùng, JWT Login/Register
│   │   │   ├── bookings.py        # Quản lý đặt phòng, vé máy bay & dịch vụ Human-in-the-Loop
│   │   │   ├── currency.py        # Tỷ giá & quy đổi tiền tệ trực tiếp (/rates, /rate, /convert)
│   │   │   ├── destinations.py    # Gợi ý điểm đến & thông tin địa phương
│   │   │   ├── flights.py         # Tra cứu chuyến bay (/search)
│   │   │   ├── hotels.py          # Tra cứu chỗ ở (/search)
│   │   │   ├── translation.py     # Dịch thuật thông minh (/translate)
│   │   │   ├── trips.py           # CRUD tour, /modify, /confirm, /versions, xuất /pdf
│   │   │   └── websocket.py       # Kênh cập nhật trạng thái thời gian thực
│   │   ├── core/                  # Cấu hình hệ thống, Database Session & Bảo mật
│   │   │   ├── config.py          # Pydantic BaseSettings & Environment variables
│   │   │   └── database.py        # SQLAlchemy Engine, SessionLocal, Seed defaults
│   │   ├── models/                # Database Models (User, Trip, Itinerary, Booking, TripVersion)
│   │   ├── schemas/               # Pydantic Schemas xác thực Input / Output
│   │   ├── services/              # Các dịch vụ nền tảng
│   │   │   ├── currency_service.py # Dịch vụ tỷ giá đa tiền tệ thế giới
│   │   │   ├── geo_service.py     # OpenStreetMap Geocoding & Airport Finder
│   │   │   ├── llm_service.py     # Tích hợp OpenAI GPT-4o & Parser thông minh
│   │   │   ├── optimizer.py       # Haversine distance, Time monotonic optimizer
│   │   │   ├── pdf_service.py     # Xuất file PDF ReportLab chuẩn Unicode Tiếng Việt
│   │   │   ├── rag_service.py     # Retrieval-Augmented Generation (ChromaDB)
│   │   │   ├── replan_service.py  # Động cơ Re-planning & Quản lý Version tour
│   │   │   ├── request_parser.py  # Bộ phân tích yêu cầu ngôn ngữ tự nhiên
│   │   │   └── translation_service.py # Dịch thuật trực tuyến + Từ điển Offline đa ngữ
│   │   └── main.py                # FastAPI Entrypoint, Circuit Breaker, CORS, Rate Limiter
│   ├── tests/                     # Bộ kiểm thử tự động Pytest (19/19 Tests)
│   │   ├── test_api.py            # Kiểm thử toàn diện API, Replan, Confirm, PDF, Search
│   │   ├── test_currency.py       # Kiểm thử chuyển đổi tiền tệ
│   │   ├── test_parser.py         # Kiểm thử nhận dạng thực thể tự nhiên
│   │   └── test_replan.py         # Kiểm thử tăng version & điều chỉnh giờ
│   ├── seed_data.py               # Nạp dữ liệu mẫu khởi đầu
│   ├── pytest.ini                 # Cấu hình test runner
│   └── requirements.txt           # Thư viện Python phụ thuộc
│
├── frontend/                      # Web Client (Next.js 16 + Tailwind CSS + TypeScript)
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   │   ├── layout.tsx         # Root Layout
│   │   │   └── page.tsx           # Dashboard chính điều phối Chat, Timeline & Utilities
│   │   ├── components/            # UI Components chuyên biệt
│   │   │   ├── ChatAgent.tsx      # Trợ lý chat AI, tách biệt lập tour vs hỏi đáp hành trình
│   │   │   ├── ItineraryTimeline.tsx # Timeline lịch trình, bộ chọn version, gợi ý điểm đến
│   │   │   ├── ReplanModal.tsx    # Modal điều chỉnh mục lịch trình & cập nhật DB
│   │   │   └── TravelUtilitiesHub.tsx # Trung tâm tiện ích: Tỷ giá, Dịch thuật, Bookings, Q&A
│   │   └── lib/                   # Thư viện kết nối API
│   │       └── api.ts             # Axios instance, Interceptors, Retry logic, Type normalization
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── mobile/                        # Mobile Companion App (React Native + Expo SDK 57)
│   ├── app/                       # Expo Router File-based Navigation
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx        # Cấu hình thanh Tab Navigation
│   │   │   ├── assistant.tsx      # Màn hình Trợ lý AI đàm thoại
│   │   │   ├── itinerary.tsx      # Màn hình Chi tiết Lịch trình & Re-plan
│   │   │   ├── services.tsx       # Màn hình Tra cứu Vé máy bay, Khách sạn, Bookings
│   │   │   ├── currency.tsx       # Màn hình Đổi ngoại tệ & Dịch thuật thông minh
│   │   │   ├── planner.tsx        # Màn hình Khởi tạo kế hoạch tour mới
│   │   │   └── settings.tsx       # Cài đặt kết nối máy chủ & Hồ sơ người dùng
│   │   └── _layout.tsx            # Root Stack Layout
│   ├── src/
│   │   ├── api/                   # Mobile API Client & Tự động nhận diện IP LAN máy chủ
│   │   ├── components/            # Modal Xác thực, Modal Sửa lịch trình, Navbar Header
│   │   ├── context/               # AuthContext lưu trữ trạng thái người dùng
│   │   └── services/              # Offline Caching (AsyncStorage) & Trip Sync
│   ├── app.json                   # Cấu hình Expo SDK 57 (com.travelagent.mobile)
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml             # Triển khai môi trường Containerized (Backend, DB, Frontend)
└── README.md                      # Tài liệu kỹ thuật chi tiết của dự án
```

---

## ✨ CÁC CHỨC NĂNG NỔI BẬT (KEY HIGHLIGHTS)

### 1. 🤖 Lập Tour Tự Động Bằng Ngôn Ngữ Tự Nhiên
- Tiếp nhận câu lệnh tự do: *"Lập tour đi Hallstatt, Áo 4 ngày 3 đêm cho 2 người từ Hà Nội, ngân sách 2.000 EUR, thích hồ và thưởng thức ẩm thực bản địa"*.
- Tự động trích xuất: Điểm khởi hành, Điểm đến, Số ngày, Ngân sách, Loại tiền tệ, Số người, Sở thích riêng biệt.
- Tự động tính toán thời gian bay thực tế theo cự ly địa lý (quốc nội, Đông Nam Á, Đông Á, liên lục địa châu Âu/châu Mỹ).

### 2. ⚡ Tối Ưu Hóa Tuyến Đường & Khung Giờ Tuyến Tính (Optimizer)
- Sắp xếp các hoạt động trong ngày theo thứ tự logic: `FLIGHT / CHECK-IN` ➔ `BỮA SÁNG` ➔ `THAM QUAN SÁNG` ➔ `BỮA TRƯA` ➔ `HOẠT ĐỘNG CHIỀU` ➔ `HOÀNG HÔN` ➔ `BỮA TỐI`.
- Chống nghịch lý nén thời gian: Chuyến bay dài tự động hạ cánh vào buổi tối (khoảng 20:30), nhận phòng lúc 20:45 - 21:45 và ăn tối nhẹ lúc 22:00 - 23:00. **Tuyệt đối không có hoạt động nào bị dồn ép giờ trùng nhau tại 23:59**.

### 3. 🔄 Re-planning Động & Lưu Trữ Phiên Bản (Trip Versioning)
- Cho phép người dùng chỉnh sửa thời gian bắt đầu, thay đổi món ăn, hoạt động hoặc hủy mục.
- Thuật toán `replan_service` tính toán lại toàn bộ các sự kiện kế tiếp trong ngày, dịch chuyển giờ ăn và khoảng đệm di chuyển.
- Tự động tạo phiên bản mới (Version 1, Version 2, Version 3...) và lưu trực tiếp vào bảng `TripVersion` trong cơ sở dữ liệu.
- Người dùng có thể xem lại lịch sử thay đổi và chuyển đổi giữa các phiên bản bất kỳ lúc nào.

### 4. 🧰 Travel Utilities Hub Đa Tiện Ích
- **Quy đổi Ngoại tệ Thời gian thực**: Hỗ trợ VND, USD, EUR, JPY, KRW, THB, CHF, GBP, SGD, AUD... với tỷ giá cập nhật liên tục.
- **Dịch thuật Du lịch Đa ngữ**: Hỗ trợ 10+ ngôn ngữ phổ biến kèm **ngân hàng từ vựng Offline an toàn** (chào hỏi, khách sạn, gọi món, trả tiền, hỏi đường, cấp cứu) hoạt động mượt mà ngay cả khi không có kết nối Internet.
- **In-Trip Assistant**: Tra cứu thời tiết, quán ăn ngon quanh khách sạn, cảnh báo an toàn và hướng dẫn phương tiện di chuyển công cộng.
- **Human-in-the-Loop Booking**: Tự động gợi ý 3 dịch vụ mẫu (Vé máy bay, Phòng nghỉ, Tour danh thắng) ở trạng thái `Chờ duyệt (PENDING)`. Người dùng có quyền bấm **Xác nhận** hoặc **Hủy bỏ** bất kỳ lúc nào.

### 5. 📄 Xuất Lịch Trình PDF Chuẩn Quốc Tế
- Tích hợp công cụ xuất PDF ReportLab chuyên nghiệp.
- Hỗ trợ đầy đủ font chữ Unicode tiếng Việt, bảng chi phí ước tính, mã đặt chỗ, thời gian biểu và ghi chú hành trình.

### 6. 📱 Mobile Companion Hoàn Thiện (Expo SDK 57)
- Ứng dụng di động được đồng bộ 100% chức năng với Web.
- Tự động nhận diện địa chỉ IP máy chủ trong mạng LAN nội bộ khi chạy trên điện thoại thật qua Expo Go.
- Lưu trữ cục bộ qua AsyncStorage, cho phép xem lại lịch trình ngay cả khi mất sóng điện thoại.

---

## 🛠️ HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY (QUICK START GUIDE)

### Yêu Cầu Môi Trường (Prerequisites)
- **Python**: Phiên bản 3.11 trở lên.
- **Node.js**: Phiên bản 18 trở lên (khuyên dùng Node.js LTS).
- **Trình quản lý gói**: `npm` hoặc `yarn`.
- **Ứng dụng trên điện thoại**: Ứng dụng **Expo Go** (Phiên bản tương thích với SDK 57 tải từ Google Play Store hoặc Apple App Store).

---

### BƯỚC 1: KHỞI ĐỘNG BACKEND SERVER

1. Mở cửa sổ Terminal (PowerShell / Command Prompt / Bash) và di chuyển vào thư mục backend:
   ```bash
   cd Travel_Agent/backend
   ```

2. Tạo và kích hoạt môi trường ảo Python (Virtual Environment):
   ```bash
   # Trên Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Trên macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

4. Nạp dữ liệu mặc định ban đầu:
   ```bash
   python seed_data.py
   ```

5. Khởi chạy máy chủ FastAPI Backend:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Trang chủ API Gateway**: `http://localhost:8000/`
   - **Tài liệu API tương tác (Swagger UI)**: `http://localhost:8000/docs`
   - **Tài liệu thay thế (ReDoc)**: `http://localhost:8000/redoc`

---

### BƯỚC 2: KHỞI ĐỘNG FRONTEND WEB APPLICATION

1. Mở một cửa sổ Terminal mới và di chuyển vào thư mục frontend:
   ```bash
   cd Travel_Agent/frontend
   ```

2. Cài đặt các gói phụ thuộc (dùng `--legacy-peer-deps` để đảm bảo tương thích hoàn hảo):
   ```bash
   npm install --legacy-peer-deps
   ```

3. Khởi chạy máy chủ phát triển Web Next.js:
   ```bash
   npm run dev
   ```

4. Mở trình duyệt web và truy cập:
   ```
   http://localhost:3000
   ```

*(Tùy chọn) Kiểm tra đóng gói phiên bản Production của Web:*
```bash
npm run build
npm run start
```

---

### BƯỚC 3: KHỞI ĐỘNG MOBILE APPLICATION (REACT NATIVE / EXPO)

1. Mở một cửa sổ Terminal thứ ba và di chuyển vào thư mục mobile:
   ```bash
   cd Travel_Agent/mobile
   ```

2. Cài đặt các gói phụ thuộc:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Khởi chạy máy chủ Expo Metro Bundler:
   ```bash
   npx expo start
   ```

4. Trải nghiệm ứng dụng trên điện thoại:
   - **Trên điện thoại Android thật**: Mở ứng dụng **Expo Go (SDK 57)**, chọn "Scan QR code" và quét mã QR trên màn hình Terminal.
   - **Trên máy ảo Android**: Nhấn phím `a` trên bàn phím Terminal.
   - **Trên máy ảo iOS**: Nhấn phím `i` trên bàn phím Terminal.
   - **Chạy trên trình duyệt Web (Expo Web)**: Nhấn phím `w` trên bàn phím Terminal.

> **💡 Lưu ý kết nối Mobile với Backend:**
> - Nếu chạy trên điện thoại thật, hãy đảm bảo máy tính và điện thoại kết nối **cùng một mạng Wi-Fi**. Ứng dụng đã tích hợp cơ chế tự động nhận diện IP máy chủ nội bộ.
> - Bạn cũng có thể vào tab **Settings** trên Mobile App để tùy chỉnh trực tiếp địa chỉ Backend IP bất cứ lúc nào (ví dụ: `http://192.168.1.15:8000/api/v1`).

---

## 🧪 KIỂM THỬ HỆ THỐNG (TESTING & QUALITY ASSURANCE)

Dự án được bảo chứng chất lượng với bộ kiểm thử tự động toàn diện:

### 1. Kiểm Thử Backend (Pytest)
Chạy toàn bộ 19 bài kiểm thử đơn vị và tích hợp:
```bash
# Đứng tại thư mục gốc hoặc thư mục backend
python -m pytest backend/tests/ -v
```
**Kết quả kiểm thử thực tế:**
```
backend/tests/test_api.py::test_root_endpoint PASSED
backend/tests/test_api.py::test_currency_rates_endpoint PASSED
backend/tests/test_api.py::test_currency_rate_pair_endpoint PASSED
backend/tests/test_api.py::test_flights_search_keys PASSED
backend/tests/test_api.py::test_hotels_search_keys PASSED
backend/tests/test_api.py::test_trips_list_endpoint PASSED
backend/tests/test_api.py::test_ai_plan_trip_flow PASSED
backend/tests/test_api.py::test_currency_cross_compatibility PASSED
backend/tests/test_api.py::test_translation_offline_phrases PASSED
backend/tests/test_api.py::test_clarification_no_destination PASSED
backend/tests/test_currency.py::test_supported_currencies PASSED
backend/tests/test_currency.py::test_exchange_rate_usd_vnd PASSED
backend/tests/test_currency.py::test_convert_currency PASSED
backend/tests/test_currency.py::test_get_all_rates PASSED
backend/tests/test_parser.py::test_japan_family_trip_prompt PASSED
backend/tests/test_parser.py::test_date_range_duration_extraction PASSED
backend/tests/test_parser.py::test_foreign_currency_budget PASSED
backend/tests/test_parser.py::test_intent_classification PASSED
backend/tests/test_replan.py::test_replan_version_increment_and_time_adjustment PASSED

============================= 19 passed in 4.79s =============================
```

### 2. Kiểm Thử Kiểu Dữ Liệu Frontend (TypeScript Next.js)
```bash
cd frontend
npm run build
```
Đạt chuẩn `Compiled successfully`, 0 lỗi TypeScript, 0 lỗi cú pháp.

### 3. Kiểm Thử Kiểu Dữ Liệu Mobile (TypeScript Expo)
```bash
cd mobile
npx tsc --noEmit
```
Đạt chuẩn `Exit code 0`, kiểm tra toàn bộ màn hình và navigation không có lỗi kiểu.

---

## ⚙️ CẤU HÌNH BIẾN MÔI TRƯỜNG (ENVIRONMENT VARIABLES)

Hệ thống có thể chạy ngay với các giá trị mặc định được định cấu hình sẵn. Khi muốn kết nối OpenAI LLM thực tế hoặc PostgreSQL, tạo file `.env` tại thư mục `backend/`:

```env
# --- AI & LLM CONFIGURATION ---
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# --- DATABASE CONFIGURATION ---
# Mặc định sử dụng SQLite cục bộ:
DATABASE_URL=sqlite:///./travel_agent.db
# Hoặc cấu hình sang PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/travel_agent_db

# --- SECURITY & JWT ---
SECRET_KEY=super_secret_jwt_key_travel_agent_2026_antigravity
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# --- TRANSLATION PROVIDER (OPTIONAL) ---
DEEPL_API_KEY=
```

---

## 🐳 TRIỂN KHAI VỚI DOCKER COMPOSE (OPTIONAL)

Nếu bạn muốn khởi chạy toàn bộ hệ sinh thái (PostgreSQL, FastAPI Backend, Next.js Frontend) chỉ bằng một câu lệnh:

```bash
docker-compose up --build
```
Hệ thống sẽ tự động cấu hình cơ sở dữ liệu, nạp font chữ tiếng Việt cho ReportLab và mở các cổng dịch vụ sẵn sàng sử dụng.

---

## ❓ GIẢI ĐÁP CÁC SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Lỗi `Project is incompatible with this version of Expo Go`**:
   - Dự án đã được nâng cấp chính thức lên **Expo SDK 57**. Hãy đảm bảo ứng dụng **Expo Go** trên điện thoại của bạn đã cập nhật lên phiên bản mới nhất từ Store.
2. **Lỗi `ERESOLVE could not resolve dependency` khi `npm install`**:
   - Sử dụng cờ `npm install --legacy-peer-deps` để giải quyết các ràng buộc chéo giữa React 18/19 của các thư viện giao diện.
3. **Lỗi không kết nối được Backend từ Mobile App**:
   - Kiểm tra xem điện thoại và máy tính có cùng một mạng Wi-Fi không.
   - Kiểm tra tường lửa Windows Firewall có đang chặn cổng `8000` hay không.
   - Nhập thủ công địa chỉ IPv4 máy tính của bạn vào mục **Settings** trên Mobile App.

---