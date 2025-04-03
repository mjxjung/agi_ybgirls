# llm_api.py
from openai import OpenAI
from dotenv import load_dotenv
import os

# 🔑 API Key 설정
load_dotenv()
client = OpenAI()

def ask_disease_recommendation(symptom: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 의학 전문 AI입니다. 사용자 증상에 맞는 질병 3가지를 추천하세요."},
            {"role": "user", "content": f"증상: {symptom}"}
        ]
    )
    content = response.choices[0].message.content
    choices = [c.strip() for c in content.split(",")[:3]]

    return {
        "message": content,
        "choices": choices
    }

def ask_doctor_info(disease: str) -> dict:
    prompt = f"""
'{disease}'에 대해 추천할 수 있는 전문의를 이름, 진료과, 전문분야로 2명 소개해주세요.
결과는 아래와 같은 딕셔너리 리스트로 표현해줘:

[
    {{"name": "이름", "department": "진료과", "specialty": "전문분야"}},
    ...
]
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 의학 전문 AI입니다. 사용자에게 친절하고 정확하게 응답하세요."},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content

    try:
        doctors = eval(text)  # LLM이 포맷 맞춰주면 OK (주의: 프로덕션에선 `ast.literal_eval()` 써야 안전)
    except:
        doctors = []

    return {
        "message": f"'{disease}' 관련 전문의를 안내드릴게요:",
        "doctors": doctors
    }
