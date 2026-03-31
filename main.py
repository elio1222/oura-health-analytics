from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from datetime import date, timedelta, timezone, datetime
from services.oura_service import fetch_oura_data

load_dotenv()

app = FastAPI()

# functions / tools to use
def param_builder(start_date: date, end_date: date) -> dict:
    return {
        "start_date": start_date,
        "end_date": end_date
    }

def calculate_readiness_summary(data: dict, params: dict) -> dict:

    scores = [d["score"] for d in data["data"]]
    activity_balance = [d["contributors"]["activity_balance"] for d in data["data"] if d != None]
    body_temperature = [d["contributors"]["body_temperature"] for d in data["data"]]
    hrv_balance = [d["contributors"]["hrv_balance"] for d in data["data"]]
    previous_day_activity = [d["contributors"]["previous_day_activity"] for d in data["data"] if d["contributors"]["previous_day_activity"] != None]
    previous_night = [d["contributors"]["previous_night"] for d in data["data"]]
    recovery_index = [d["contributors"]["recovery_index"] for d in data["data"]]
    resting_heart_rate = [d["contributors"]["resting_heart_rate"] for d in data["data"]]
    sleep_balance = [d["contributors"]["sleep_balance"] for d in data["data"]]
    sleep_regularity = [d["contributors"]["sleep_regularity"] for d in data["data"]]

    # unpacking parameter
    week_from_td, today = params.values()

    readiness_stats = {
        "dates": {
            "start_date": week_from_td,
            "end_date": today
        },
        "avg_scores": {
            "score": round(sum(scores) / len(scores), 2),
            "activity_balance": round(sum(activity_balance) / len(activity_balance), 2),
            "body_temperature": round(sum(body_temperature) / len(body_temperature), 2),
            "hrv_balance": round(sum(hrv_balance) / len(hrv_balance), 2),
            "previous_day_activity": round(sum(previous_day_activity) / len(previous_day_activity), 2),
            "previous_night": round(sum(previous_night) / len(previous_night), 2),
            "recovery_index": round(sum(recovery_index) / len(recovery_index), 2),
            "resting_heart_rate": round(sum(resting_heart_rate) / len(resting_heart_rate), 2),
            "sleep_balance": round(sum(sleep_balance) / len(sleep_balance), 2),
            "sleep_regularity": round(sum(sleep_regularity) / len(sleep_regularity), 2)
        }
    }

    return readiness_stats


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


"""Daily Sleep"""
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


"""Daily Readiness"""
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
def get_latest_readiness():
    """Get latest readiness data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"
    params = { 
        "start_date": today, 
        "end_date": today 
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/readiness/summary")
def get_readiness_summary():
    today = date.today()
    week_from_td = today - timedelta(days=7)
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"
    params = {
        "start_date": week_from_td,
        "end_date": today
    }
    data = fetch_oura_data(url=url, params=params)
    

    scores = [d["score"] for d in data["data"]]
    activity_balance = [d["contributors"]["activity_balance"] for d in data["data"] if d != None]
    body_temperature = [d["contributors"]["body_temperature"] for d in data["data"]]
    hrv_balance = [d["contributors"]["hrv_balance"] for d in data["data"]]
    previous_day_activity = [d["contributors"]["previous_day_activity"] for d in data["data"] if d["contributors"]["previous_day_activity"] != None]
    previous_night = [d["contributors"]["previous_night"] for d in data["data"]]
    recovery_index = [d["contributors"]["recovery_index"] for d in data["data"]]
    resting_heart_rate = [d["contributors"]["resting_heart_rate"] for d in data["data"]]
    sleep_balance = [d["contributors"]["sleep_balance"] for d in data["data"]]
    sleep_regularity = [d["contributors"]["sleep_regularity"] for d in data["data"]]

    readiness_stats = {
        "dates": {
            "start_date": week_from_td,
            "end_date": today
        },
        "avg_scores": {
            "score": round(sum(scores) / len(scores), 2),
            "activity_balance": round(sum(activity_balance) / len(activity_balance), 2),
            "body_temperature": round(sum(body_temperature) / len(body_temperature), 2),
            "hrv_balance": round(sum(hrv_balance) / len(hrv_balance), 2),
            "previous_day_activity": round(sum(previous_day_activity) / len(previous_day_activity), 2),
            "previous_night": round(sum(previous_night) / len(previous_night), 2),
            "recovery_index": round(sum(recovery_index) / len(recovery_index), 2),
            "resting_heart_rate": round(sum(resting_heart_rate) / len(resting_heart_rate), 2),
            "sleep_balance": round(sum(sleep_balance) / len(sleep_balance), 2),
            "sleep_regularity": round(sum(sleep_regularity) / len(sleep_regularity), 2)
        }
    }

    return readiness_stats

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

"""Daily Stress"""
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

"""Personal Info"""
@app.get("/user/")
def get_personal_info():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/personal_info"
    params = {
        "start_date": today,
        "end_date": today
    }
    return fetch_oura_data(url=url, params=params)

"""Heart Rate"""
@app.get("/heart-rate/latest")
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

"""Sleep Periods (Routes in Oura API Docs)"""
@app.get("/periods/sleep/")
def get_sleep_routes(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/sleep"
    params = { 
        "start_date": start_date, 
        "end_date": end_date 
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/periods/sleep/latest")
def get_latest_sleep_routes():
    today = date.today()
    yesterday = today - timedelta(days=1)
    url = "https://api.ouraring.com/v2/usercollection/sleep"

    params = {
    "start_date": yesterday,
    "end_date": today
    }

    return fetch_oura_data(url=url, params=params)


from services.ai_assistant import analyze_oura_analytics

@app.get("/health-assistant/insight")
def get_health_assistant_insight():
    params = param_builder(start_date=date.today() - timedelta(days=6), end_date=date.today())

    sleep_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_sleep", params=params)

    readiness_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_readiness", params=params)

    stress_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_stress", params=params)

    sleep_readiness_stress_data = {
        "sleep_data": sleep_data,
        "readiness_data": readiness_data,
        "stress_data": stress_data
    }

    return analyze_oura_analytics(user_data=sleep_readiness_stress_data)

