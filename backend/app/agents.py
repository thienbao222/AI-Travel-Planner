import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import settings

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set!")

# ==========================================
# 1. FLIGHT AGENT SCHEMA & LOGIC
# ==========================================
class TransportOption(BaseModel):
    carrier: str = Field(description="Tên hãng vận chuyển hoặc loại xe/tàu (VD: Vietnam Airlines, Phương Trang)")
    price_estimate: float = Field(description="Chi phí ước tính bằng VND")
    duration: str = Field(description="Thời gian di chuyển ước tính (VD: 1h 30m, 6h)")
    departure_time: str = Field(description="Giờ khởi hành gợi ý (VD: 07:00 AM)")
    arrival_time: str = Field(description="Giờ đến dự kiến (VD: 08:30 AM)")
    pros_cons: str = Field(description="Ưu và nhược điểm ngắn gọn")

class FlightAgentResponse(BaseModel):
    transport_type: str = Field(description="Phương tiện chủ đạo (VD: Máy bay, Xe khách, Tàu hỏa)")
    options: List[TransportOption]
    recommended_option_index: int = Field(description="Index của tùy chọn tối ưu nhất (0-indexed)")

def call_flight_agent(origin: str, destination: str, start_date: str, end_date: str, budget: float) -> FlightAgentResponse:
    prompt = f"""
    Bạn là Flight Agent chuyên trách phương tiện di chuyển trong hệ thống Multi-Agent Travel Planner.
    Hãy đề xuất các phương tiện di chuyển từ '{origin}' đến '{destination}' cho chuyến đi từ ngày {start_date} đến {end_date}.
    Ngân sách tối đa của hành khách là {budget:,} VND.
    Hãy đề xuất ít nhất 2 phương án di chuyển khả thi nhất (ví dụ: máy bay nếu muốn nhanh, xe khách/tàu hỏa nếu muốn tiết kiệm).
    Các ước tính giá vé phải mang tính thực tế.
    """
    
    model = genai.GenerativeModel(
        model_name=settings.DEFAULT_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": FlightAgentResponse
        }
    )
    
    response = model.generate_content(prompt)
    return FlightAgentResponse.model_validate_json(response.text)


# ==========================================
# 2. HOTEL AGENT SCHEMA & LOGIC
# ==========================================
class HotelRecommendation(BaseModel):
    name: str = Field(description="Tên khách sạn hoặc Homestay")
    type: str = Field(description="Loại hình (Khách sạn 3 sao, Homestay, Resort, v.v.)")
    address: str = Field(description="Địa chỉ hoặc khu vực (VD: Phường 2, gần Hồ Xuân Hương)")
    price_per_night: float = Field(description="Giá một đêm bằng VND")
    total_price: float = Field(description="Tổng giá tiền lưu trú cho cả chuyến đi bằng VND")
    amenities: List[str] = Field(description="Các tiện ích nổi bật (VD: Wifi, Bữa sáng, Thuê xe máy)")
    why_recommended: str = Field(description="Lý do đề xuất khách sạn này")

class HotelAgentResponse(BaseModel):
    recommendations: List[HotelRecommendation]
    recommended_index: int = Field(description="Index của khách sạn đề xuất tối ưu nhất")

def call_hotel_agent(destination: str, duration_days: int, budget: float, preferences: str) -> HotelAgentResponse:
    prompt = f"""
    Bạn là Hotel Agent chuyên trách đặt phòng lưu trú.
    Hãy đề xuất ít nhất 2 nơi lưu trú (Khách sạn, Homestay hoặc Resort) tại '{destination}' cho chuyến đi kéo dài {duration_days} ngày ({duration_days - 1} đêm).
    Tổng ngân sách của khách là {budget:,} VND (ngân sách lưu trú nên chiếm khoảng 25-35% tổng ngân sách).
    Sở thích của khách: {preferences}.
    Giá cả đề xuất phải thực tế và phù hợp với ngân sách của hành khách.
    """
    
    model = genai.GenerativeModel(
        model_name=settings.DEFAULT_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": HotelAgentResponse
        }
    )
    
    response = model.generate_content(prompt)
    return HotelAgentResponse.model_validate_json(response.text)


# ==========================================
# 3. WEATHER AGENT SCHEMA & LOGIC
# ==========================================
class DailyWeather(BaseModel):
    day: int = Field(description="Số thứ tự ngày của chuyến đi (1, 2, 3...)")
    temp_range: str = Field(description="Khoảng nhiệt độ (VD: 16°C - 24°C)")
    condition: str = Field(description="Tình trạng thời tiết chính (VD: Nắng ráo, Mưa rào, Có sương mù)")
    activity_suitability: str = Field(description="Mức độ phù hợp hoạt động ngoài trời (Rất tốt, Khá tốt, Hạn chế)")

class WeatherAgentResponse(BaseModel):
    forecast: List[DailyWeather]
    luggage_tips: List[str] = Field(description="Gợi ý hành lý và trang phục phù hợp")
    general_warnings: Optional[str] = Field(description="Cảnh báo đặc biệt về thời tiết nếu có (VD: Có mưa giông lớn về chiều)")

def call_weather_agent(destination: str, start_date: str, duration_days: int) -> WeatherAgentResponse:
    prompt = f"""
    Bạn là Weather Agent chuyên cung cấp thông tin thời tiết du lịch.
    Hãy dự báo thời tiết tại '{destination}' bắt đầu từ ngày {start_date} cho {duration_days} ngày tiếp theo.
    (Lưu ý: Nếu đây là thời gian tương lai, hãy đưa ra dự báo dựa trên khí hậu lịch sử và xu hướng mùa của địa điểm đó).
    Đồng thời đưa ra gợi ý chuẩn bị trang phục, hành lý và các cảnh báo thời tiết đặc biệt để hỗ trợ khách hàng lên kế hoạch đi chơi an toàn.
    """
    
    model = genai.GenerativeModel(
        model_name=settings.DEFAULT_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": WeatherAgentResponse
        }
    )
    
    response = model.generate_content(prompt)
    return WeatherAgentResponse.model_validate_json(response.text)


# ==========================================
# 4. ITINERARY AGENT SCHEMA & LOGIC
# ==========================================
class Activity(BaseModel):
    time_slot: str = Field(description="Thời gian/Khung giờ (VD: 08:00 - 10:00 hoặc Sáng)")
    description: str = Field(description="Mô tả chi tiết hoạt động (Đi đâu, làm gì)")
    location: str = Field(description="Địa điểm diễn ra hoạt động")
    estimated_cost: float = Field(description="Chi phí phát sinh cho hoạt động này (VND), nếu miễn phí ghi 0")

class DailyItinerary(BaseModel):
    day: int = Field(description="Ngày thứ mấy (1, 2, 3...)")
    title: str = Field(description="Tiêu đề chính của ngày này (VD: Khám phá Trung tâm & Cafe lãng mạn)")
    morning: List[Activity]
    afternoon: List[Activity]
    evening: List[Activity]
    route_optimization: str = Field(description="Giải thích ngắn gọn cách tối ưu hóa tuyến đường di chuyển trong ngày (VD: Đi các điểm cùng hướng phía Bắc để tránh đi ngược đường)")

class ItineraryAgentResponse(BaseModel):
    daily_plans: List[DailyItinerary]

def call_itinerary_agent(
    destination: str, 
    duration_days: int, 
    weather_summary: str, 
    hotel_location: str, 
    arrival_departure_times: str,
    preferences: str
) -> ItineraryAgentResponse:
    prompt = f"""
    Bạn là Itinerary Agent chuyên lập lịch trình chi tiết và tối ưu hóa tuyến đường.
    Hãy thiết lập lịch trình du lịch {duration_days} ngày tại '{destination}' đáp ứng các thông tin đầu vào sau:
    - Vị trí Khách sạn lưu trú: {hotel_location} (Bắt đầu và kết thúc các ngày từ đây để tối ưu hóa quãng đường).
    - Thời gian đến và đi: {arrival_departure_times} (Hãy sắp xếp ngày 1 bắt đầu sau giờ đến và ngày cuối kết thúc trước giờ đi).
    - Điều kiện thời tiết: {weather_summary} (Nếu ngày nào mưa nhiều, hãy xếp hoạt động trong nhà, bảo tàng, cafe; ngày nắng ráo xếp hoạt động ngoài trời).
    - Sở thích hành khách: {preferences}.
    
    Hãy đảm bảo lịch trình thực tế, có thời gian nghỉ ngơi, các điểm đến trong cùng một buổi sáng hoặc chiều phải gần nhau về mặt địa lý.
    """
    
    model = genai.GenerativeModel(
        model_name=settings.DEFAULT_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": ItineraryAgentResponse
        }
    )
    
    response = model.generate_content(prompt)
    return ItineraryAgentResponse.model_validate_json(response.text)


# ==========================================
# 5. BUDGET AGENT SCHEMA & LOGIC
# ==========================================
class BudgetAllocation(BaseModel):
    transportation: float = Field(description="Chi phí di chuyển (VND)")
    accommodation: float = Field(description="Chi phí lưu trú (VND)")
    activities: float = Field(description="Chi phí tham quan, vui chơi (VND)")
    food_and_beverage: float = Field(description="Chi phí ăn uống ước tính (VND)")
    contingency: float = Field(description="Chi phí dự phòng (VND)")

class BudgetAgentGeminiResponse(BaseModel):
    transportation_cost: float = Field(description="Chi phí di chuyển (VND)")
    accommodation_cost: float = Field(description="Chi phí lưu trú (VND)")
    activities_cost: float = Field(description="Chi phí tham quan, vui chơi (VND)")
    food_and_beverage_cost: float = Field(description="Chi phí ăn uống ước tính (VND)")
    contingency_cost: float = Field(description="Chi phí dự phòng (VND)")
    total_cost: float = Field(description="Tổng chi phí dự toán (bằng tổng các mục trên)")
    status: str = Field(description="Trạng thái ngân sách (VD: Nằm trong ngân sách, Vượt nhẹ ngân sách, Vượt quá ngân sách)")
    saving_tips: List[str] = Field(description="Gợi ý cắt giảm chi phí cụ thể cho chuyến đi này")
    is_feasible: bool = Field(description="Đánh giá kế hoạch tài chính này có khả thi không")

class BudgetAgentResponse(BaseModel):
    allocation: BudgetAllocation = Field(description="Bảng phân bổ ngân sách chi tiết")
    total_cost: float = Field(description="Tổng chi phí dự toán (bằng tổng các mục trên)")
    status: str = Field(description="Trạng thái ngân sách (VD: Nằm trong ngân sách, Vượt nhẹ ngân sách, Vượt quá ngân sách)")
    saving_tips: List[str] = Field(description="Gợi ý cắt giảm chi phí cụ thể cho chuyến đi này")
    is_feasible: bool = Field(description="Đánh giá kế hoạch tài chính này có khả thi không")

def call_budget_agent(
    budget_limit: float, 
    flight_cost: float, 
    hotel_cost: float, 
    estimated_activity_cost: float,
    duration_days: int
) -> BudgetAgentResponse:
    prompt = f"""
    Bạn là Budget Agent chịu trách nhiệm tính toán phân bổ và tối ưu hóa tài chính cho chuyến đi.
    - Ngân sách tối đa của hành khách: {budget_limit:,} VND.
    - Chi phí di chuyển cố định (Flight/Bus): {flight_cost:,} VND.
    - Chi phí lưu trú cố định (Hotel): {hotel_cost:,} VND.
    - Tổng chi phí các hoạt động vui chơi đề xuất: {estimated_activity_cost:,} VND.
    - Số ngày du lịch: {duration_days} ngày.
    
    Hãy tính toán và phân bổ chi phí ăn uống hợp lý cho {duration_days} ngày (thường khoảng 200,000 - 400,000 VND/ngày/người tùy địa điểm), 
    cộng thêm một khoản chi phí dự phòng (thường 5-10% tổng ngân sách).
    
    Sau đó, hãy tính Tổng chi phí dự kiến. Đưa ra đánh giá xem kế hoạch chi tiêu này có nằm trong giới hạn {budget_limit:,} VND không.
    Nếu vượt ngân sách, đề xuất các mẹo tiết kiệm thông minh.
    """
    
    model = genai.GenerativeModel(
        model_name=settings.DEFAULT_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": BudgetAgentGeminiResponse
        }
    )
    
    response = model.generate_content(prompt)
    gemini_res = BudgetAgentGeminiResponse.model_validate_json(response.text)
    
    return BudgetAgentResponse(
        allocation=BudgetAllocation(
            transportation=gemini_res.transportation_cost,
            accommodation=gemini_res.accommodation_cost,
            activities=gemini_res.activities_cost,
            food_and_beverage=gemini_res.food_and_beverage_cost,
            contingency=gemini_res.contingency_cost
        ),
        total_cost=gemini_res.total_cost,
        status=gemini_res.status,
        saving_tips=gemini_res.saving_tips,
        is_feasible=gemini_res.is_feasible
    )
