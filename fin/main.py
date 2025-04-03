from embedding import embedding_symptoms, compute_disease_symptom_embeddings
from similarity import similarity_symptoms
from summarization import summarize_symptoms
from recommendation import get_recommended_doctors
from data_loader import load_doctor_data
import os
from dotenv import load_dotenv

load_dotenv()

base_path = './Database/embedding'
json_folder = 'agi_ybgirls/Database/output/processed_final'
embedding_csv_path = os.path.join(base_path, "disease_embeddings.csv")

# 질병 임베딩 사전 저장 (최초 1회 실행)
compute_disease_symptom_embeddings(json_folder, embedding_csv_path)
print('질병 임베딩 완료')

# 환자 증상 입력
patient_symptoms = "우리 아기가 수유 장애가 있고, 귀에 물이 고여요. 말을 하기 힘들어해요."
patient_emb = embedding_symptoms(patient_symptoms)

# 유사 질병 추천 : top-k 3개로 설정
best_matches = similarity_symptoms(patient_emb, embedding_csv_path)

top_disease = list(best_matches.keys())[0]
second_disease = list(best_matches.keys())[1]
third_disease = list(best_matches.keys())[2]

# 첫번째 추천 질병의 의사 정보 불러오기
doctor_info_df_1, doctor_recommendation_df_1 = load_doctor_data(base_path)
doctor_info_1 = get_recommended_doctors(
    top_disease,
    os.path.join(base_path, "doctor_recommendation.csv"),
    os.path.join(base_path, "doctor_info.csv")
)
# 두번째 추천 질병의 의사 정보 불러오기
doctor_info_df_2, doctor_recommendation_df_2 = load_doctor_data(base_path)
doctor_info_2 = get_recommended_doctors(
    second_disease,
    os.path.join(base_path, "doctor_recommendation.csv"),
    os.path.join(base_path, "doctor_info.csv")
)
# 세번째 추천 질병의 의사 정보 불러오기
doctor_info_df_3, doctor_recommendation_df_3 = load_doctor_data(base_path)
doctor_info_3 = get_recommended_doctors(
    third_disease,
    os.path.join(base_path, "doctor_recommendation.csv"),
    os.path.join(base_path, "doctor_info.csv")
)

# 증상 요약
summary_1 = summarize_symptoms(patient_symptoms)
summary_2 = summarize_symptoms(patient_symptoms)
summary_3 = summarize_symptoms(patient_symptoms)

# 최종 출력
print(f"환자 증상: {patient_symptoms}")
print(f"환자 증상 요약: {summarize_symptoms(patient_symptoms)}")
print()
print(f"가장 유사한 질병: {top_disease}")
print(f"증상 요약: {summary_1}")
print(f"추천 의사 정보: {doctor_info_1}")
print()
print(f"두번째로 유사한 질병: {second_disease}")
print(f"증상 요약: {summary_2}")
print(f"추천 의사 정보: {doctor_info_2}")
print()
print(f"가장 유사한 질병: {third_disease}")
print(f"증상 요약: {summary_3}")
print(f"추천 의사 정보: {doctor_info_3}")
print()

