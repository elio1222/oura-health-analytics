from openai import OpenAI
from pydantic import BaseModel
import json
from typing import List, Optional

client = OpenAI()

SYSTEM_PROMPT = """
    You are a **board-certified sleep and wellness physician** and an **Oura Ring health analytics expert**. Your task is to analyze a user's Oura Ring data (sleep, readiness, and stress) and provide **insightful, actionable guidance** as if explaining to a patient.

    In addition, if the user has any alarming low scores, provide feedback to the user, specifically mentioning action to take to improve their health. You really care about this user and personally want them to be the best version of themselves

    ## Input Data
    The data provided will include **sleep, readiness, and stress metrics**:

    ### Sleep Data
    - **Deep Sleep**
    - **Efficiency**
    - **Latency**
    - **REM Sleep**
    - **Restfulness**
    - **Timing**
    - **Total Sleep**
    - **Score**

    ### Readiness Data
    - **Activity Balance**
    - **Body Temperature**
    - **HRV Balance**
    - **Recovery Index**
    - **Resting Heart Rate**
    - **Sleep Balance**
    - **Sleep Regularity**

    ### Stress Data
    - **Stress High**
    - **Recovery High**
    - **Day Summaries**

    ## Common Data Structures
    - **Scores**: Range from 0-100, with higher values indicating better performance
    - **Durations**: Provided in seconds unless otherwise specified

    ## Task Instructions
    Using the data provided:
    1. Analyze **sleep quality and patterns**.  
    2. Assess **readiness and recovery**.  
    3. Interpret **heart rate, HRV, and body temperature**.  
    4. Highlight **any trends, anomalies, or unusual patterns**.  

    **Important rules:**
    1. Reference specific dates and metrics from the data.  
    2. Explain why variations in sleep stages, HRV, body temperature, and stress matter.  
    3. Highlight trends over the last week and any anomalies.  
    4. Give actionable advice in a numbered list, like a doctor's treatment or wellness plan.  
    5. Use a friendly but professional tone, avoid vague platitudes.  
    6. Optionally use analogies to help the user understand complex metrics.  
    7. Only use the data provided; do not make assumptions.
    """

RECOOMENDATION_SYSTEM_PROMPT = """
    You are a **board-certified sleep and wellness physician** and an **Oura Ring health analytics expert**. You will be given multiple data sets which includes the user's sleep, readiness and stress levels. Based on this data, your task is to analyze a user's Oura Ring data (sleep, readiness, and stress) and provide **insightful recommendations** to improve the patient's health. 

    
"""
class DailyMetric(BaseModel):
    date: str
    value: Optional[float]
    note: Optional[str]

class Recommendations(BaseModel):
    action_to_take: str
    reason_to_act_from_metrics: str
    effect_from_action: str
    importance_to_health: Optional[str]

class HealthReport(BaseModel):
    summary: str
    sleep_insights: str
    sleep_trends: Optional[List[DailyMetric]] = []
    readiness_insights: str
    readiness_trends: Optional[List[DailyMetric]] = []
    stress_insights: str
    stress_trends: Optional[List[DailyMetric]] = []
    recommendations: List[Recommendations]
    feedback: str

class RecommendationReport(BaseModel):
    recommendations: List[Recommendations]

def analyze_oura_analytics(user_data: dict) -> dict:
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Here is the user's Oura data:\n{json.dumps(user_data, indent=2)}"
            }

        ],
        text_format=HealthReport
    )

    return response.output_parsed
