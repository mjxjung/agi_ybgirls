import pandas as pd

def get_recommended_doctors(disease_name, rec_csv_path, info_csv_path):
    rec_df = pd.read_csv(rec_csv_path, encoding="cp949")
    info_df = pd.read_csv(info_csv_path, encoding="utf-8")

    rec_row = rec_df[rec_df['병명'] == disease_name]
    if rec_row.empty:
        return {}

    recommended_info = {}
    for col in ['추천의사1', '추천의사2', '추천의사3']:
        doctor = rec_row.iloc[0].get(col)
        if pd.isna(doctor) or not doctor.strip():
            break
        info_row = info_df[info_df['doc_name'] == doctor]
        if info_row.empty:
            continue
        recommended_info[doctor] = {
            "doc_name": info_row.iloc[0]["doc_name"],
            "dept_name": info_row.iloc[0]["dept_name"],
            "special_disease": info_row.iloc[0]["special_disease"]
        }

    return recommended_info
