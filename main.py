from fastapi import FastAPI, HTTPException
from datetime import date

app = FastAPI()

# Fake database (temporary)
TODAY_DATA = {
    "A001": {
        "demand_level": "High",
        "workload_minutes": 90,
        "advice_message": "High day. Do 1 deep block, then recovery + early sleep."
    },
    "A002": {
        "demand_level": "Low",
        "workload_minutes": 30,
        "advice_message": "Low day. Light work, tidy tasks, protect energy."
    },
    "CJ01": {
        "demand_level": "Medium",
        "workload_minutes": 60,
        "advice_message": "Medium day. Two focused blocks (30–45 min), stop before cutoff."
    }
}

@app.get("/")
def root():
    return {"status": "Athlete API running"}

@app.get("/today/{athlete_id}")
def today(athlete_id: str):
    athlete_id = athlete_id.upper().strip()

    if athlete_id not in TODAY_DATA:
        raise HTTPException(status_code=404, detail="Athlete not found")

    data = TODAY_DATA[athlete_id]
    return {
        "athlete_id": athlete_id,
        "date": str(date.today()),
        **data
    }
