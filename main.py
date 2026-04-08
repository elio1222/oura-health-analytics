from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from datetime import date, timedelta, timezone, datetime
from services.oura_service import fetch_oura_data, run, get_tokens
import services.db_service as db
from services.analytics_service import calculate_sleep_summary, calculate_readiness_summary, param_builder
from services.ai_service import analyze_oura_analytics

load_dotenv()

app = FastAPI()

if not os.getenv("ACCESS_TOKEN") or not os.getenv("REFRESH_TOKEN"):
    run()

@app.get('/callback')
def callback(code: str = None):
    if code:
        get_tokens(code)
        return {"message": "Authorization successful. You can close this tab."}
    else:
        return {"error": "No code found in URL"}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Oura Analytics</title>
        </head>
        <body>
            <h1>Elio Rocha's Oura Health Analytics REST API</h1>
        </body>
    </html>
    """

"""Daily Sleep"""
@app.get("/sleep/")
async def get_sleep(start_date: str, end_date: str):
    """Get sleep data from specified start and end dates"""
    return db.query_from_db(type_of_data="sleep", params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/sleep/latest")
def get_latest_sleep():
    """Get latest sleep data(max retries 3)"""
    today = datetime.now(timezone.utc).date()
    return db.query_from_db(type_of_data="sleep", params=param_builder(start_date=today, end_date=today))

@app.get("/sleep/summary")
def get_sleep_summary():
    """Get sleep summary data from the past 7 days, returns avg score"""
    return calculate_sleep_summary()

"""Daily Readiness"""
@app.get("/readiness/")
async def get_readiness(start_date: str, end_date: str):
    """Get readiness data from specified start and end dates"""

    url = "https://api.ouraring.com/v2/usercollection/daily_readiness" 

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/readiness/latest")
def get_latest_readiness():
    """Get latest readiness data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

@app.get("/readiness/summary")
def get_readiness_summary():
    today = date.today()
    week_from_td = today - timedelta(days=7)
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"

    data = fetch_oura_data(url=url, params=param_builder(start_date=week_from_td, end_date=today))
    readiness_stats = calculate_readiness_summary(data=data, params=param_builder(start_date=week_from_td, end_date=today))

    return readiness_stats

"""Daily Activity"""
@app.get("/activity/")
def get_activity(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/activity/latest")
def get_latest_activity():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

"""Daily Stress"""
@app.get("/stress/")
def get_stress(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/stress/latest")
def get_latest_stress():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

@app.get("/stress/summary")
def get_stress_summary():
    yesterday = date.today() - timedelta(days=1)
    week_from_td = yesterday - timedelta(days=6)
    url = "https://api.ouraring.com/v2/usercollection/daily_stress"

    data = fetch_oura_data(url=url, params=param_builder(start_date=week_from_td, end_date=yesterday))
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

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

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

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/periods/sleep/latest")
def get_latest_sleep_routes():
    today = date.today()
    yesterday = today - timedelta(days=1)
    url = "https://api.ouraring.com/v2/usercollection/sleep"

    return fetch_oura_data(url=url, params=param_builder(start_date=yesterday, end_date=today))

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

