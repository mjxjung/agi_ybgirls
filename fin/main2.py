from embedding import embedding_symptoms, compute_disease_symptom_embeddings
from similarity import similarity_symptoms
from summarization import summarize_symptoms
from recommendation import get_recommended_doctors
from data_loader import load_doctor_data
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# 기본 경로 설정
base_path = './Database/embedding'
json_folder = 'agi_ybgirls/Database/output/processed_final'
embedding_csv_path = os.path.join(base_path, "disease_embeddings.csv")
recommendation_csv_path = os.path.join(base_path, "doctor_recommendation.csv")
info_csv_path = os.path.join(base_path, "doctor_info.csv")

# 최초 1회만 수행
compute_disease_symptom_embeddings(json_folder, embedding_csv_path)
print('질병 임베딩 완료')


def get_top_disease_candidates(symptom: str) -> list[dict]:
    patient_emb = embedding_symptoms(symptom)
    best_matches = similarity_symptoms(patient_emb, embedding_csv_path)
    top_3_diseases = list(best_matches.keys())[:3]

    candidates = []
    for disease_name in top_3_diseases:
        result = summarize_symptoms(symptom)
        summary = result["output_text"] if isinstance(result, dict) and "output_text" in result else str(result)
        candidates.append({
            "name": disease_name,
            "description": summary
        })
    return candidates


def get_doctor_info_by_diseases(disease_list: list) -> dict:
    doctor_info_map = {}
    for disease in disease_list:
        doctor_dict = get_recommended_doctors(disease, recommendation_csv_path, info_csv_path)

        # 🔁 딕셔너리를 리스트로 변환
        doctor_list = []
        for doctor_name, info in doctor_dict.items():
            doctor_list.append({
                "name": info["doc_name"],
                "department": info["dept_name"],
                "specialty": info["special_disease"]
            })

        doctor_info_map[disease] = {
            "message": f"{disease}에 맞는 의사를 추천해드릴게요.",
            "doctors": doctor_list
        }
    return doctor_info_map


def build_response(symptom: str, disease_candidates: list[dict], doctor_info_map: dict) -> dict:
    return {
        "symptom": symptom,
        "disease_candidates": disease_candidates,
        "doctors_by_disease": doctor_info_map
    }


def get_disease_and_doctors(symptom: str) -> dict:
    disease_candidates = get_top_disease_candidates(symptom)
    disease_names = [d["name"] for d in disease_candidates]
    doctor_info_map = get_doctor_info_by_diseases(disease_names)
    return build_response(symptom, disease_candidates, doctor_info_map)