import os
import pandas as pd
import json

def load_doctor_data(base_path):
    doctor_info_df = pd.read_csv(os.path.join(base_path, "doctor_info.csv"), encoding="utf-8")
    doctor_recommendation_df = pd.read_csv(os.path.join(base_path, "doctor_recommendation.csv"), encoding="cp949")
    return doctor_info_df, doctor_recommendation_df

def load_disease_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
