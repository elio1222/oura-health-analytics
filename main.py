from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from datetime import date, timedelta, timezone, datetime
from services.oura_service import fetch_oura_data

load_dotenv()

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Oura Analytics</title>
        </head>
        <body>
            <h1>Elio Rocha's Oura Health Analytics</h1>
        </body>
    </html>
    """


"""Daily Sleep Routes"""
@app.get("/sleep/")
async def get_sleep(start_date: str, end_date: str):
    """Get sleep data from specified start and end dates
    Args:
        start_date (str): beginning date
        end_date (str): end date
    """

    url = "https://api.ouraring.com/v2/usercollection/daily_sleep" 
    params={ 
        "start_date": start_date, 
        "end_date": end_date 
    }

    return fetch_oura_data(url=url, params=params)

@app.get("/sleep/latest")
def get_latest_sleep():
    """Get latest sleep data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    params = {
        "start_date": today,
        "end_date": today
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/sleep/summary")
def get_sleep_summary():
    """Get sleep summary data from the past 7 days, returns avg score"""

    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    data = fetch_oura_data(url=url, params=params)
    
    score = 0
    for d in data["data"]:
        score += d["score"]
    avg_score = score / len(data["data"])

    json_data = {
        "avg_score": avg_score,
        "days_tracked": len(data["data"])
    }

    return json_data

"""Sleep Routes"""
@app.get("/sleep/routes")
def get_sleep_routes(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/sleep"
    params = { 
        "start_date": start_date, 
        "end_date": end_date 
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/sleep/routes/latest")
def get_latest_sleep_routes():
    today = date.today()
    yesterday = today - timedelta(days=1)
    url = "https://api.ouraring.com/v2/usercollection/sleep"

    params = {
    "start_date": yesterday,
    "end_date": today
    }

    return fetch_oura_data(url=url, params=params)


"""Readiness Routes"""
@app.get("/readiness/")
async def get_readiness(start_date: str, end_date: str):
    """Get readiness data from specified start and end dates
    Args:
        start_date (str): beginning date
        end_date (str): end date
    """

    url = "https://api.ouraring.com/v2/usercollection/daily_readiness" 
    params={ 
        "start_date": start_date, 
        "end_date": end_date 
    }

    return fetch_oura_data(url=url, params=params)

@app.get("/readiness/latest")
def get_readiness_sleep():
    """Get latest readiness data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"
    params = { 
        "start_date": today, 
        "end_date": today 
    }
    return fetch_oura_data(url=url, params=params)

"""Daily Activity"""
@app.get("/activity/")
def get_activity(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/activity/latest")
def get_latest_activity():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"
    params = {
        "start_date": today,
        "end_date": today
    }
    return fetch_oura_data(url=url, params=params)

"""Personal Info"""
@app.get("/info/")
def get_personal_info():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/personal_info"
    params = {
        "start_date": today,
        "end_date": today
    }
    return fetch_oura_data(url=url, params=params)

"""Heart Rate"""
@app.get("/bpm/")
def get_bpm():
    now = datetime.now().astimezone()
    earlier = now - timedelta(minutes=60)
    now = now.replace(microsecond=0).isoformat()
    earlier = earlier.replace(microsecond=0).isoformat()
    url = "https://api.ouraring.com/v2/usercollection/heartrate"

    params = {
        "start_datetime": earlier,
        "end_datetime": now
    }
    print(params)
    return fetch_oura_data(url=url, params=params)
"""Sleep Time"""


"""Stress"""
@app.get("/stress/")
def get_stress(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/stress/latest")
def get_latest_stress():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"
    params = {
        "start_date": today,
        "end_date": today
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/stress/summary")
def get_stress_summary():
    yesterday = date.today() - timedelta(days=1)
    week_from_td = yesterday - timedelta(days=6)
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"
    params = {
        "start_date": week_from_td,
        "end_date": yesterday
    }

    data = fetch_oura_data(url=url, params=params)
    if data.get("data") and len(data.get("data")) > 0:

        recovery_high = 0
        stress_high = 0
        day_summary = {
            "stressful": 0,
            "restored": 0,
            "normal": 0
        }
        length = 0

        for scores in data["data"]:
            if scores["day_summary"] is None:
                continue
            recovery_high += scores["recovery_high"]
            stress_high += scores["stress_high"]
            day_summary.setdefault(scores["day_summary"], 0)
            day_summary[scores["day_summary"]] += 1
            length += 1

        avg_recovery = recovery_high / length
        avg_stress = stress_high / length


    return {
        "dates": {
            "start_date": week_from_td,
            "end_date": yesterday
        },
        "avg_recovery": round(avg_recovery / 3600, 2),
        "avg_stress": round(avg_stress / 3600, 2),
        "day_summaries": day_summary
    }
