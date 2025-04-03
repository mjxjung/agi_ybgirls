import csv
import json
from utils import cosine_similarity

def similarity_symptoms(patient_embeddings, csv_path, top_k=3):
    embedding_data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["embedding"] = json.loads(row["embedding"])
            embedding_data.append(row)

    similarities = []
    for entry in embedding_data:
        sim = cosine_similarity(patient_embeddings, entry["embedding"])
        similarities.append((entry["disease"], sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return {disease: sim for disease, sim in similarities[:top_k]}
