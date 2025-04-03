import os
import json
import uuid
from glob import glob
from tqdm import tqdm

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

def load_json_as_documents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for entry in data:
        # if entry.get("section") != "증상":  # ✅ 증상 섹션 필터링
        #     continue
        
        content = entry.get("embedding_text") or entry.get("content")
        if not content:
            print(f"⚠️ content 없음 → 건너뜀: {entry.get('disease')} - {entry.get('section')}")
            continue
        doc = Document(
            page_content=content,
            metadata={
                "disease": entry.get("disease", "unknown"),
                "section": entry.get("section", "unknown")
            }
        )
        documents.append(doc)
    return documents

def embed_and_save_faiss(documents, index_path, embedding_model):
    faiss_index = FAISS.from_documents(documents, embedding_model)
    os.makedirs(index_path, exist_ok=True)
    faiss_index.save_local(index_path)

def process_all_files(json_folder, output_folder, mapping_path):
    json_files = glob(os.path.join(json_folder, "*.json"))
    if not json_files:
        print("❌ JSON 파일이 존재하지 않습니다.")
        return

    os.makedirs(output_folder, exist_ok=True)
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index_mapping = {}

    for file_path in tqdm(json_files, desc="✅ 전체 질병 처리 중"):
        try:
            disease_name = os.path.splitext(os.path.basename(file_path))[0]
            unique_id = str(uuid.uuid4())[:8]
            folder_name = f"index_{unique_id}"
            index_path = os.path.join(output_folder, folder_name)

            documents = load_json_as_documents(file_path)
            if not documents:
                print(f"⚠️ 문서 없음 → 건너뜀: {disease_name}")
                continue

            embed_and_save_faiss(documents, index_path, embedding_model)
            index_mapping[disease_name] = folder_name
            print(f"✅ 저장 완료: {disease_name} → {folder_name}")
        except Exception as e:
            print(f"❌ 처리 실패: {file_path} → {e}")

    # 매핑 정보 저장
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(index_mapping, f, ensure_ascii=False, indent=2)
    print(f"✅ 인덱스 매핑 저장 완료: {mapping_path}")

if __name__ == "__main__":
    json_folder = "Database/output/processed_final"
    output_folder = "Database/faiss_index"
    mapping_path = os.path.join(output_folder, "index_mapping.json")

    process_all_files(json_folder, output_folder, mapping_path)
