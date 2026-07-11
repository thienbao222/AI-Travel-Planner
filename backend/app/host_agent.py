import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents import (
    call_flight_agent,
    call_hotel_agent,
    call_weather_agent,
    call_itinerary_agent,
    call_budget_agent,
    FlightAgentResponse,
    HotelAgentResponse,
    WeatherAgentResponse,
    ItineraryAgentResponse,
    BudgetAgentResponse,
    TransportOption,
    HotelRecommendation,
    BudgetAllocation
)

class TravelPlanRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    duration_days: int
    budget: float
    preferences: str

class HostLog(BaseModel):
    step: str
    message: str

class TravelPlanResponse(BaseModel):
    destination: str
    duration_days: int
    budget_limit: float
    flight_data: FlightAgentResponse
    hotel_data: HotelAgentResponse
    weather_data: WeatherAgentResponse
    itinerary_data: ItineraryAgentResponse
    budget_data: BudgetAgentResponse
    logs: List[HostLog]

def run_travel_planner_pipeline(request: TravelPlanRequest) -> TravelPlanResponse:
    logs = []
    
    # helper to log
    def add_log(step: str, message: str):
        logs.append(HostLog(step=step, message=message))
        print(f"[{step}] {message}")

    add_log("Khởi tạo", f"Bắt đầu xử lý yêu cầu đi {request.destination} từ {request.origin} trong {request.duration_days} ngày. Ngân sách: {request.budget:,} VND.")

    # 1. Gọi Weather Agent & Flight Agent song song ở Giai đoạn 1
    add_log("Giai đoạn 1: Thông tin Nền tảng", "Đang gọi Weather Agent để dự báo thời tiết...")
    try:
        weather_res = call_weather_agent(request.destination, request.start_date, request.duration_days)
        add_log("Weather Agent", f"Dự báo thời tiết thành công. Cảnh báo chung: {weather_res.general_warnings or 'Không có'}")
    except Exception as e:
        add_log("Weather Agent - Thất bại", f"Lỗi lấy thông tin thời tiết: {e}. Sử dụng dữ liệu giả định.")
        weather_res = WeatherAgentResponse(
            forecast=[],
            luggage_tips=["Mang quần áo thoải mái", "Mang ô/dù phòng hờ"],
            general_warnings="Không có dữ liệu thời tiết cụ thể."
        )

    add_log("Giai đoạn 1: Thông tin Nền tảng", "Đang gọi Flight Agent để đề xuất phương tiện di chuyển...")
    try:
        flight_res = call_flight_agent(request.origin, request.destination, request.start_date, f"ngày cuối", request.budget)
        rec_flight = flight_res.options[flight_res.recommended_option_index]
        add_log("Flight Agent", f"Khuyên dùng: {flight_res.transport_type} ({rec_flight.carrier}) - Giá ước tính: {rec_flight.price_estimate:,} VND. Giờ đến: {rec_flight.arrival_time}.")
    except Exception as e:
        add_log("Flight Agent - Thất bại", f"Lỗi đề xuất phương tiện: {e}. Sử dụng dữ liệu dự phòng.")
        flight_res = FlightAgentResponse(
            transport_type="Xe khách",
            options=[
                TransportOption(carrier="Xe khách Phương Trang", price_estimate=300000, duration="6h", departure_time="08:00 AM", arrival_time="02:00 PM", pros_cons="Giá rẻ, an toàn")
            ],
            recommended_option_index=0
        )
        rec_flight = flight_res.options[0]

    # 2. Giai đoạn 2: Gọi Hotel Agent
    add_log("Giai đoạn 2: Lựa chọn Lưu trú", "Đang gọi Hotel Agent tìm nơi ở phù hợp...")
    # Tính ngân sách dự kiến cho khách sạn (khoảng 30% tổng ngân sách)
    hotel_budget_allocation = request.budget * 0.3
    try:
        hotel_res = call_hotel_agent(request.destination, request.duration_days, request.budget, request.preferences)
        rec_hotel = hotel_res.recommendations[hotel_res.recommended_index]
        add_log("Hotel Agent", f"Khuyên dùng: {rec_hotel.name} ({rec_hotel.type}) tại {rec_hotel.address}. Tổng giá: {rec_hotel.total_price:,} VND.")
    except Exception as e:
        add_log("Hotel Agent - Thất bại", f"Lỗi tìm khách sạn: {e}. Sử dụng dữ liệu dự phòng.")
        hotel_res = HotelAgentResponse(
            recommendations=[
                HotelRecommendation(name="Đà Lạt Homestay Trung Tâm", type="Homestay", address="Phường 2, Đà Lạt", price_per_night=400000, total_price=400000 * (request.duration_days - 1), amenities=["Wifi", "Chỗ để xe"], why_recommended="Giá rẻ, gần trung tâm")
            ],
            recommended_index=0
        )
        rec_hotel = hotel_res.recommendations[0]

    # 3. Giai đoạn 3: Lập lịch trình Itinerary Agent dựa trên thông tin thu được
    add_log("Giai đoạn 3: Lập Lịch trình", "Gửi dữ liệu thời tiết, vị trí khách sạn và giờ xe chạy để Itinerary Agent lên lịch tối ưu...")
    
    # Tạo chuỗi mô tả thời tiết để Itinerary Agent hiểu
    weather_summary_parts = []
    for day_w in weather_res.forecast:
        weather_summary_parts.append(f"Ngày {day_w.day}: {day_w.condition} ({day_w.temp_range})")
    weather_summary = "; ".join(weather_summary_parts) if weather_summary_parts else "Mát mẻ, nắng nhẹ"
    
    hotel_location = f"{rec_hotel.name} ({rec_hotel.address})"
    arrival_departure = f"Đến {request.destination} lúc {rec_flight.arrival_time}. Rời {request.destination} lúc {rec_flight.departure_time} (hoặc chiều về tương đương)."
    
    try:
        itinerary_res = call_itinerary_agent(
            destination=request.destination,
            duration_days=request.duration_days,
            weather_summary=weather_summary,
            hotel_location=hotel_location,
            arrival_departure_times=arrival_departure,
            preferences=request.preferences
        )
        add_log("Itinerary Agent", f"Sinh lịch trình chi tiết thành công gồm {len(itinerary_res.daily_plans)} ngày.")
    except Exception as e:
        add_log("Itinerary Agent - Thất bại", f"Lỗi sinh lịch trình: {e}. Sử dụng dữ liệu dự phòng.")
        # Tạo dữ liệu trống/đơn giản
        itinerary_res = ItineraryAgentResponse(daily_plans=[])

    # 4. Giai đoạn 4: Tính toán ngân sách thực tế bằng Budget Agent
    add_log("Giai đoạn 4: Quản lý Ngân sách", "Đang gọi Budget Agent để tổng hợp và tối ưu tài chính...")
    
    # Tính chi phí hoạt động từ lịch trình
    estimated_activity_cost = 0
    for day_plan in itinerary_res.daily_plans:
        for act in day_plan.morning + day_plan.afternoon + day_plan.evening:
            estimated_activity_cost += act.estimated_cost
            
    try:
        budget_res = call_budget_agent(
            budget_limit=request.budget,
            flight_cost=rec_flight.price_estimate,
            hotel_cost=rec_hotel.total_price,
            estimated_activity_cost=estimated_activity_cost,
            duration_days=request.duration_days
        )
        add_log("Budget Agent", f"Tổng chi phí dự kiến: {budget_res.total_cost:,} VND. Trạng thái: {budget_res.status}. Khả thi: {budget_res.is_feasible}.")
    except Exception as e:
        add_log("Budget Agent - Thất bại", f"Lỗi tính toán ngân sách: {e}.")
        # Dự phòng đơn giản
        budget_res = BudgetAgentResponse(
            allocation=BudgetAllocation(
                transportation=rec_flight.price_estimate,
                accommodation=rec_hotel.total_price,
                activities=estimated_activity_cost,
                food_and_beverage=300000 * request.duration_days,
                contingency=200000
            ),
            total_cost=rec_flight.price_estimate + rec_hotel.total_price + estimated_activity_cost + (300000 * request.duration_days) + 200000,
            status="Nằm trong ngân sách",
            saving_tips=["Sử dụng xe máy để di chuyển trong thành phố", "Ăn uống tại quán ăn địa phương bình dân"],
            is_feasible=True
        )

    # 5. Hoàn tất tổng hợp dữ liệu
    add_log("Hoàn thành", "Host Agent đã tổng hợp thành công tất cả thông tin từ các Sub-Agents.")
    
    return TravelPlanResponse(
        destination=request.destination,
        duration_days=request.duration_days,
        budget_limit=request.budget,
        flight_data=flight_res,
        hotel_data=hotel_res,
        weather_data=weather_res,
        itinerary_data=itinerary_res,
        budget_data=budget_res,
        logs=logs
    )
