# Đề tài Nhóm 4: Multi-Agent AI Travel Planner trên Google Cloud Platform

Dự án này là một hệ thống lập kế hoạch du lịch thông minh sử dụng kiến trúc **Multi-Agent** (Đa tác tử) dựa trên **Google Gemini API**, được triển khai bằng **FastAPI (Backend)** và **Streamlit (Frontend)**, sẵn sàng để deploy lên **Google Cloud Run** thông qua Docker.

---

## 🏗️ Kiến Trúc Hệ Thống (Multi-Agent)

Hệ thống được thiết kế theo mô hình điều phối tuần tự kết hợp song song để tránh xung đột dữ liệu:

1. **Host Agent**: Tiếp nhận yêu cầu thô từ khách hàng (điểm đến, thời gian, ngân sách, sở thích).
2. **Giai đoạn 1 (Thông tin nền)**: Host Agent gọi đồng thời **Flight Agent** (gợi ý phương tiện & giờ di chuyển) và **Weather Agent** (cung cấp dự báo thời tiết).
3. **Giai đoạn 2 (Định vị lưu trú)**: Host Agent chuyển ngân sách & sở thích cho **Hotel Agent** đề xuất nơi ở phù hợp.
4. **Giai đoạn 3 (Lập lịch trình)**: Host Agent tổng hợp *Thời tiết + Giờ tàu xe + Vị trí khách sạn* để gửi cho **Itinerary Agent**, giúp sinh lịch trình chi tiết (Sáng/Chiều/Tối) tối ưu hóa quãng đường di chuyển thực tế.
5. **Giai đoạn 4 (Kiểm soát ngân sách)**: Host Agent gửi toàn bộ chi phí thực tế cho **Budget Agent** tính toán phân bổ ăn uống, quỹ dự phòng và đánh giá tính khả thi tài chính.
6. **Tổng hợp**: Host Agent đóng gói toàn bộ phản hồi gửi về cho Frontend.

---

## 📂 Cấu Trúc Thư Mục

```text
travel_planner/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py       # Cấu hình & Đọc biến môi trường
│   │   ├── agents.py       # Khởi tạo Pydantic Schemas & gọi Gemini API cho Sub-Agents
│   │   ├── host_agent.py   # Quy trình điều phối của Host Agent
│   │   └── main.py         # REST API của FastAPI (Expose các Agent endpoint)
│   ├── Dockerfile          # Dockerfile đa giai đoạn tối ưu cho Cloud Run
│   └── requirements.txt
├── frontend/
│   ├── app.py              # Giao diện Streamlit tương tác
│   ├── Dockerfile          # Dockerfile Streamlit cho Cloud Run
│   └── requirements.txt
├── docker-compose.yml      # Chạy thử local tiện lợi
├── .env.example            # Mẫu file cấu hình môi trường
└── README.md               # Tài liệu hướng dẫn
```

---

## 🚀 Hướng Dẫn Chạy Thử Local

### 1. Sử dụng Docker Compose (Khuyên dùng)

1. Sao chép file `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```
2. Điền Key của bạn vào biến `GEMINI_API_KEY` trong file `.env` (Lấy key tại [Google AI Studio](https://aistudio.google.com/)).
3. Khởi động hệ thống bằng docker-compose:
   ```bash
   docker compose up --build
   ```
4. Truy cập giao diện:
   - **Frontend Streamlit**: [http://localhost:8501](http://localhost:8501)
   - **Backend FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Chạy tay bằng Python (Không dùng Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Set biến môi trường GEMINI_API_KEY (Ví dụ PowerShell: $env:GEMINI_API_KEY="your-key")
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
python -m venv venv
source venv/Scripts/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Mặc định kết nối tới http://localhost:8000
streamlit run app.py --server.port 8501
```

---

## ☁️ Hướng Dẫn Triển Khai Lên Google Cloud Platform (GCP)

Dưới đây là quy trình từng bước để nhóm deploy ứng dụng lên **Google Cloud Run**.

### Bước 1: Chuẩn bị môi trường & GCP Project
1. Đăng nhập và cài đặt Google Cloud SDK (gcloud CLI) trên máy cá nhân.
2. Thiết lập project làm việc mặc định:
   ```bash
   gcloud config set project [PROJECT_ID]
   ```
3. Bật các API cần thiết:
   ```bash
   gcloud services enable run.googleapis.com \
                          artifactregistry.googleapis.com \
                          secretmanager.googleapis.com \
                          cloudbuild.googleapis.com
   ```

### Bước 2: Lưu Gemini API Key vào Secret Manager
Để bảo mật tốt nhất theo tiêu chuẩn Cloud, ta lưu API Key vào Secret Manager:
```bash
echo -n "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets create GEMINI_API_KEY --data-file=-
```
Cấp quyền đọc Secret cho Cloud Run Service Account mặc định (thường là Compute Engine Service Account hoặc Service Account bạn tự tạo).

### Bước 3: Tạo Artifact Registry và Build Image bằng Cloud Build

1. Tạo Registry chứa Docker Images:
   ```bash
   gcloud artifacts repositories create travel-planner-repo \
       --repository-format=docker \
       --location=asia-southeast1 \
       --description="Docker repository for Travel Planner"
   ```

2. Build & Push Backend Image lên Registry:
   ```bash
   cd backend
   gcloud builds submit --tag asia-southeast1-docker.pkg.dev/[PROJECT_ID]/travel-planner-repo/backend:latest .
   ```

3. Build & Push Frontend Image lên Registry:
   ```bash
   cd ../frontend
   gcloud builds submit --tag asia-southeast1-docker.pkg.dev/[PROJECT_ID]/travel-planner-repo/frontend:latest .
   ```

### Bước 4: Deploy lên Google Cloud Run

1. **Triển khai Backend:**
   ```bash
   gcloud run deploy travel-planner-backend \
       --image=asia-southeast1-docker.pkg.dev/[PROJECT_ID]/travel-planner-repo/backend:latest \
       --region=asia-southeast1 \
       --allow-unauthenticated \
       --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest
   ```
   *Sau khi hoàn tất lệnh này, GCP sẽ trả về một URL công khai cho Backend. Hãy copy URL đó (Ví dụ: `https://travel-planner-backend-xxxxx-as.a.run.app`).*

2. **Triển khai Frontend:**
   ```bash
   gcloud run deploy travel-planner-frontend \
       --image=asia-southeast1-docker.pkg.dev/[PROJECT_ID]/travel-planner-repo/frontend:latest \
       --region=asia-southeast1 \
       --allow-unauthenticated \
       --set-env-vars=BACKEND_URL=[COPY_URL_BACKEND_Ở_TRÊN]
   ```
   *GCP sẽ trả về một URL công khai cho Frontend Streamlit. Hãy click vào URL này để kiểm nghiệm ứng dụng chạy trực tiếp trên Cloud!*

### Bước 5: Theo dõi Log trên GCP
- Các thông tin debug của Host Agent và A2A simulation được xuất ra Console và được tự động ghi lại tại **Cloud Logging**.
- Bạn có thể xem trực tiếp log của container bằng cách vào trang dịch vụ Cloud Run trên GCP Console và chọn tab **LOGS**.
