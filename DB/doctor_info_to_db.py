import pandas as pd
import sqlite3

# 파일 경로
csv_path = "doctor_info.csv"           # CSV 파일 경로
db_path = "disease_doctor.db"                 # DB 파일 경로

# CSV 불러오기
df = pd.read_csv(csv_path)

# 컬럼명 바꾸기 (CSV 기준 → DB 기준)
df = df.rename(columns={
    "doc_name": "name",
    "dept_name": "department",
    "special_disease": "specialty"
})


# DB 연결
conn = sqlite3.connect(db_path)

# doctors 테이블에 저장 (있으면 덮어쓰기)
df.to_sql("doctors", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("✅ doctors 테이블에 CSV 데이터 저장 완료!")
