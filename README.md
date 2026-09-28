# HỆ THỐNG TRAVEL AGENT AI (DỰ ÁN ĐỒ ÁN CHUYÊN SÂU)

> **Tên Đồ Án:** Xây dựng Travel Agents dùng cho mục đích tự lập kế hoạch tour, đặt dịch vụ và hỗ trợ khách trong hành trình.
> **Công nghệ:** Python (FastAPI, LangGraph, LangChain, ChromaDB RAG, SQLAlchemy) • Next.js 14 • React Native / Expo • ReportLab PDF.

---

## 📁 THƯ MỤC DỰ ÁN (PROJECT STRUCTURE)

```
Travel_Agent/
├── backend/                  # FastAPI + LangGraph AI Server + RAG + SQLite/PostgreSQL
│   ├── app/
│   │   ├── api/              # REST Endpoints (Auth, Destinations, Trips, Agent, Bookings)
│   │   ├── agent/            # LangGraph Core (State, Nodes, Graph, Tools)
│   │   ├── core/             # Configuration, Database Session, JWT Security
│   │   ├── models/           # SQLAlchemy DB Schemas (User, Destination, Trip, Itinerary, Booking)
│   │   ├── schemas/          # Pydantic Request/Response Models
│   │   └── services/         # RAG Vector Search, Haversine/TSP Optimizer, PDF Exporter
│   ├── seed_data.py          # Script khởi tạo Database & RAG Vector Index
│   ├── test_agent.py         # Script kiểm thử luồng thực thi của LangGraph Agent
│   └── requirements.txt      # Thư viện Python phụ thuộc
│
├── frontend/                 # Web Application (Next.js 14 App Router + Tailwind CSS)
│   ├── src/
│   │   ├── app/              # Next.js Pages (Dashboard, Layout)
│   │   ├── components/       # UI Components (ChatAgent, ItineraryTimeline, ReplanModal, InTripSupport)
│   │   └── lib/              # API Client Connector (Axios)
│   ├── package.json
│   └── tailwind.config.js
│
├── mobile/                   # Mobile Application Companion (React Native / Expo)
│   ├── App.js                # React Native Main Application Component
│   ├── src/                  # Mobile API Helper & Components
│   └── package.json
│
└── README.md                 # Hướng dẫn chi tiết dự án
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG (QUICK START)

### 1. Khởi chạy Backend Server (Python FastAPI + LangGraph)
```bash
cd backend

# Khởi tạo dữ liệu mẫu & RAG Vector Index
python seed_data.py

# Khởi chạy Uvicorn Backend API
uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`

### 2. Khởi chạy Web Client (Next.js 14)
```bash
cd frontend

# Khởi chạy Web Application
npm run dev
```
- Truy cập giao diện Web: `http://localhost:3000`

### 3. Khởi chạy Mobile App (React Native / Expo)
```bash
cd mobile

# Khởi chạy Expo Server
npx expo start
```

---

## 🌟 CÁC TÍNH NĂNG NỔI BẬT

1. **AI Travel Agent Tiếp Nhận Mục Tiêu Tự Nhiên**: Nhập văn bản tự do (Ví dụ: *"Đi Đà Nẵng 3N2Đ từ Hà Nội, 10 triệu cho 2 người, thích ẩm thực và biển"*).
2. **Retrieval-Augmented Generation (RAG)**: Truy vấn tri thức địa phương từ ChromaDB Vector Database.
3. **Route & Time Optimization**: Tự động tính khoảng cách mặt cầu Haversine và áp dụng thuật toán TSP Heuristic để sắp xếp thứ tự tham quan tối ưu khoảng cách & thời gian di chuyển.
4. **Dynamic Re-planner**: Cho phép chỉnh sửa 1 thành phần lịch trình, Agent tự động cập nhật và điều chỉnh các thành phần liên quan.
5. **In-Trip Support Assistant**: Hỗ trợ nhắc lịch, vị trí GPS thực tế và đề xuất địa điểm ăn uống, giải trí mở cửa gần vị trí người dùng.
6. **PDF Itinerary Export**: Xuất lịch trình du lịch chuyên nghiệp dưới dạng file PDF.
