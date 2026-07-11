from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from app.config import settings
from app.host_agent import run_travel_planner_pipeline, TravelPlanRequest, TravelPlanResponse
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
    BudgetAgentResponse
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent AI Travel Planner Backend using Google ADK/A2A Concepts",
    version="1.0.0"
)

# Enable CORS for Streamlit Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to Streamlit's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "framework": "FastAPI",
        "description": "Backend is running and ready to orchestrate AI Agents."
    }

# ==========================================
# A2A SIMULATED SUB-AGENT ENDPOINTS
# ==========================================

class FlightRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    budget: float

@app.post("/api/agents/flight", response_model=FlightAgentResponse, tags=["Sub-Agents"])
def flight_agent_endpoint(payload: FlightRequest):
    try:
        return call_flight_agent(
            origin=payload.origin,
            destination=payload.destination,
            start_date=payload.start_date,
            end_date=payload.end_date,
            budget=payload.budget
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class HotelRequest(BaseModel):
    destination: str
    duration_days: int
    budget: float
    preferences: str

@app.post("/api/agents/hotel", response_model=HotelAgentResponse, tags=["Sub-Agents"])
def hotel_agent_endpoint(payload: HotelRequest):
    try:
        return call_hotel_agent(
            destination=payload.destination,
            duration_days=payload.duration_days,
            budget=payload.budget,
            preferences=payload.preferences
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WeatherRequest(BaseModel):
    destination: str
    start_date: str
    duration_days: int

@app.post("/api/agents/weather", response_model=WeatherAgentResponse, tags=["Sub-Agents"])
def weather_agent_endpoint(payload: WeatherRequest):
    try:
        return call_weather_agent(
            destination=payload.destination,
            start_date=payload.start_date,
            duration_days=payload.duration_days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ItineraryRequest(BaseModel):
    destination: str
    duration_days: int
    weather_summary: str
    hotel_location: str
    arrival_departure_times: str
    preferences: str

@app.post("/api/agents/itinerary", response_model=ItineraryAgentResponse, tags=["Sub-Agents"])
def itinerary_agent_endpoint(payload: ItineraryRequest):
    try:
        return call_itinerary_agent(
            destination=payload.destination,
            duration_days=payload.duration_days,
            weather_summary=payload.weather_summary,
            hotel_location=payload.hotel_location,
            arrival_departure_times=payload.arrival_departure_times,
            preferences=payload.preferences
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BudgetRequest(BaseModel):
    budget_limit: float
    flight_cost: float
    hotel_cost: float
    estimated_activity_cost: float
    duration_days: int

@app.post("/api/agents/budget", response_model=BudgetAgentResponse, tags=["Sub-Agents"])
def budget_agent_endpoint(payload: BudgetRequest):
    try:
        return call_budget_agent(
            budget_limit=payload.budget_limit,
            flight_cost=payload.flight_cost,
            hotel_cost=payload.hotel_cost,
            estimated_activity_cost=payload.estimated_activity_cost,
            duration_days=payload.duration_days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# HOST AGENT ORCHESTRATION ENDPOINT
# ==========================================

@app.post("/api/plan", response_model=TravelPlanResponse, tags=["Orchestrator"])
def generate_travel_plan(payload: TravelPlanRequest):
    """
    Host Agent endpoint that orchestrates the execution of all Sub-Agents.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY is not configured on the server. Please set it in Secret Manager or environment variables."
        )
    try:
        return run_travel_planner_pipeline(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
