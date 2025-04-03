from embedding import embedding_symptoms, compute_disease_symptom_embeddings
from similarity import similarity_symptoms
from summarization import summarize_symptoms
from recommendation import get_recommended_doctors
from data_loader import load_doctor_data
import os
from dotenv import load_dotenv

load_dotenv()

base_path = './Database/embedding'
json_folder = os.path.join(base_path, "json")
embedding_csv_path = os.path.join(base_path, "disease_embeddings.csv")
recommendation_csv_path = os.path.join(base_path, "doctor_recommendation.csv")
info_csv_path = os.path.join(base_path, "doctor_info.csv")

# 질병 임베딩 사전 저장 (최초 1회 실행)
compute_disease_symptom_embeddings(json_folder, embedding_csv_path)
print('질병 임베딩 완료')

def get_top_disease_candidates(symptom: str) -> list:
    patient_emb = embedding_symptoms(symptom)
    best_matches = similarity_symptoms(patient_emb, embedding_csv_path)
    top_3_diseases = list(best_matches.keys())[:3]

    disease_candidates = []
    for disease_name in top_3_diseases:
        desc = summarize_symptoms(symptom, disease_name)
        disease_candidates.append({
            "name": disease_name,
            "description": desc
        })

    return disease_candidates

def get_doctor_info_by_diseases(disease_list: list) -> dict:
    doctor_info_map = {}
    for disease in disease_list:
        doctors = get_recommended_doctors(disease, recommendation_csv_path, info_csv_path)
        doctor_info_map[disease] = {
            "message": f"{disease}에 맞는 의사를 추천해드릴게요.",
            "doctors": [
                {
                    "name": doc["name"],
                    "department": doc["department"],
                    "specialty": doc["specialty"]
                }
                for doc in doctors
            ]
        }
    return doctor_info_map

def build_response(symptom: str, disease_candidates: list, doctor_info_map: dict) -> dict:
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
