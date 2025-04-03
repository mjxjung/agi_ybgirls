# build_index.py
import sqlite3
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# 설정
DB_PATH = "disease.db"
INDEX_PATH = "disease.index"
model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")

# 질병 설명 불러오기
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT description FROM diseases ORDER BY id")
descriptions = [row[0] for row in cursor.fetchall()]
conn.close()

# 임베딩 생성
embeddings = model.encode(descriptions)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))
faiss.write_index(index, INDEX_PATH)

print("✅ FAISS 인덱스 생성 완료")
