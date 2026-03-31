from openai import OpenAI
from pydantic import BaseModel
import json

client = OpenAI()

SYSTEM_PROMPT = """
    You are an **expert Oura Ring health analyst**. Your task is to analyze a user's Oura data and provide clear, actionable insights in **plain language**.

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
    ## Task Instructions

    Using the data provided:
    1. Analyze **sleep quality and patterns**.  
    2. Assess **readiness and recovery**.  
    3. Interpret **heart rate, HRV, and body temperature**.  
    4. Highlight **any trends, anomalies, or unusual patterns**.  

    **Important rules:**
    - Only use the data provided — **do not make assumptions** beyond it.  
    - Keep the insights **simple, actionable, and friendly**.  
    - Focus on providing practical advice the user can understand.
    """

class Insight(BaseModel):
    summary: str
    sleep_insights: str
    readiness_insights: str
    stress_insights: str
    recommendations: str

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
        text_format=Insight
    )

    return response.output_parsed
