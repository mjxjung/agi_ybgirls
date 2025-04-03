import os
import glob
import json
import csv
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings_model = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

def embedding_symptoms(symptom):
    return embeddings_model.embed_query(symptom)

def compute_disease_symptom_embeddings(json_folder, output_csv):
    disease_embeddings = {}
    json_files = glob.glob(os.path.join(json_folder, "*.json"))

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for entry in data:
                    if entry.get("section") == "증상":
                        disease_name = entry.get("disease")
                        content = entry.get("content")
                        if disease_name and content and disease_name not in disease_embeddings:
                            embedding_vector = embeddings_model.embed_query(content)
                            disease_embeddings[disease_name] = json.dumps(embedding_vector)

    with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["disease", "embedding"])
        writer.writeheader()
        for disease, emb_str in disease_embeddings.items():
            writer.writerow({"disease": disease, "embedding": emb_str})
