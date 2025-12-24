from fastapi import FastAPI, HTTPException
from datetime import date
from typing import Dict, Any

app = FastAPI(title="Athlete API", version="0.1.0")

# Fake database for now (we'll upgrade to a real DB next)
ATHLETES: Dict[str, Dict[str, Any]] = {
    "CJ01": {"name": "CJ", "team": "West Bedford", "sport": "Basketball"},
    "A001": {"name": "Test Athlete", "team": "Demo", "sport": "Basketball"},
}

# Today’s workload/advice per athlete (per ID)
TODAY_DATA: Dict[str, Dict[str, Any]] = {
    "CJ01": {
        "demand_level": "High",
        "workload_minutes": 90,
        "advice_message": "High-demand day. Do 1–2 focused school blocks early, then recovery + sleep priority."
    },
    "A001": {
        "demand_level": "Low",
        "workload_minutes": 30,
        "advice_message": "Low-demand day. Push school work hard (2–3 blocks), get ahead."
    },
}

@app.get("/")
def root():
    return {"status": "Athlete API running"}

@app.get("/athletes")
def list_athletes():
    return {"athletes": list(ATHLETES.keys())}

@app.get("/today/{athlete_id}")
def today(athlete_id: str):
    athlete_id = athlete_id.upper().strip()

    if athlete_id not in ATHLETES:
        raise HTTPException(status_code=404, detail="Athlete not found")

    if athlete_id not in TODAY_DATA:
        raise HTTPException(status_code=404, detail="No workload for athlete today")

    data = TODAY_DATA[athlete_id]
    return {
        "athlete_id": athlete_id,
        "date": str(date.today()),
        "profile": ATHLETES[athlete_id],
        **data
    }

from pydantic import BaseModel

class DailyLog(BaseModel):
    demand_level: str
    workload_minutes: int
    advice_message: str


@app.post("/today/{athlete_id}")
def log_today(athlete_id: str, log: DailyLog):
    athlete_id = athlete_id.upper().strip()

    if athlete_id not in ATHLETES:
        raise HTTPException(status_code=404, detail="Athlete not found")

    TODAY_DATA[athlete_id] = log.dict()
    return {
        "status": "saved",
        "athlete_id": athlete_id,
        "data": TODAY_DATA[athlete_id]
    }

