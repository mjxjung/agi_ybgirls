import sqlite3
import pandas as pd

# DB 연결
conn = sqlite3.connect("disease_doctor.db")

# doctors 테이블 불러오기
df = pd.read_sql_query("SELECT * FROM doctors", conn)

# 확인용 출력
print(df.head())  # 처음 5개만 보기

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM doctors")
count = cursor.fetchone()[0]

print(f"총 의사 수: {count}명")

conn.close()
