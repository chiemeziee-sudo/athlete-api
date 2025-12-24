from fastapi import FastAPI, HTTPException
from datetime import date
from typing import Dict, List, Any

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
# Stores full history per athlete
LOGS: Dict[str, List[Dict[str, Any]]] = {}
def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def compute_7day_metrics(history):
    """
    history: list of entries like {"date": "...", "workload_minutes": 60, ...}
    Returns: avg minutes, total minutes, last3 avg, trend (up/down), fatigue_score 0-100
    """
    last7 = history[-7:] if history else []
    mins = [_safe_int(h.get("workload_minutes", 0)) for h in last7]
    total = sum(mins)
    avg = total / len(mins) if mins else 0

    last3 = mins[-3:]
    last3_avg = (sum(last3) / len(last3)) if last3 else 0

    # simple trend: compare last3 avg vs overall avg
    trend = "up" if last3_avg > avg + 5 else "down" if last3_avg < avg - 5 else "flat"

    # fatigue score (simple but useful): weighted recent load
    # cap at 100
    fatigue = min(100, int((0.6 * last3_avg + 0.4 * avg) * 100 / 120))  # assumes 120 mins is "very high"
    return {
        "days_counted": len(mins),
        "total_minutes": total,
        "avg_minutes": round(avg, 1),
        "last3_avg_minutes": round(last3_avg, 1),
        "trend": trend,
        "fatigue_score": fatigue
    }

def recommendation_from_fatigue(fatigue_score):
    if fatigue_score >= 75:
        return {
            "demand_level": "High",
            "school_blocks": "1–2 blocks (25–35 min) early, then stop.",
            "training_note": "Keep skills short + sharp. Prioritize sleep + recovery."
        }
    if fatigue_score >= 45:
        return {
            "demand_level": "Medium",
            "school_blocks": "2 blocks (30–45 min). Stop before cutoff.",
            "training_note": "Normal work, but don’t add extra volume."
        }
    return {
        "demand_level": "Low",
        "school_blocks": "2–3 blocks (45–60 min). Push academics today.",
        "training_note": "Good day to add skill work or lifting."
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

    entry = {
        "date": str(date.today()),
        **log.dict()
    }

    TODAY_DATA[athlete_id] = log.dict()
    LOGS.setdefault(athlete_id, []).append(entry)

    return {
        "status": "saved",
        "athlete_id": athlete_id,
        "data": entry
    }
@app.get("/history/{athlete_id}")
def get_history(athlete_id: str):
    athlete_id = athlete_id.upper().strip()

    if athlete_id not in ATHLETES:
        raise HTTPException(status_code=404, detail="Athlete not found")

    return {
        "athlete_id": athlete_id,
        "history": LOGS.get(athlete_id, [])
    }
@app.get("/insights/{athlete_id}")
def insights(athlete_id: str):
    athlete_id = athlete_id.upper().strip()

    if athlete_id not in ATHLETES:
        raise HTTPException(status_code=404, detail="Athlete not found")

    history = LOGS.get(athlete_id, [])
    metrics = compute_7day_metrics(history)
    rec = recommendation_from_fatigue(metrics["fatigue_score"])

    return {
        "athlete_id": athlete_id,
        "profile": ATHLETES[athlete_id],
        "metrics_7day": metrics,
        "recommendation": rec
    }



