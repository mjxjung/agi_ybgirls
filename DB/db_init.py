import sqlite3

# 생성할 DB 파일 이름
db_path = "disease.db"

# DB 연결 및 테이블 생성
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# diseases 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    summary TEXT,
    description TEXT,
    department TEXT,
    doctor_names TEXT
)
""")

# doctors 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT,
    specialty TEXT
)
""")

conn.commit()
conn.close()

print("✅ disease.db가 생성되고, 테이블도 준비되었습니다.")
