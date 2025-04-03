import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")

PDF_ROOT_DIR = "Database/diseaseinfo"
OUTPUT_DIR = "Database/input"

# 📄 문서 파싱 함수
def call_document_parse_text_only(input_file, json_output_file):
    response = requests.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {API_KEY}"},
        data={"base64_encoding": "['figure']"},
        files={"document": open(input_file, "rb"), "model": (None, "document-parse")}
    )

    if response.status_code == 200:
        parsed = response.json()
        os.makedirs(os.path.dirname(json_output_file), exist_ok=True)
        with open(json_output_file, "w", encoding="utf-8") as f_json:
            json.dump(parsed, f_json, ensure_ascii=False, indent=2)
        print(f"✅ 저장 완료: {json_output_file}")
    else:
        print(f"❌ {input_file} 처리 실패: {response.status_code}")
        print(response.text)

# 🔄 crop 폴더 순회
for folder_name in os.listdir(PDF_ROOT_DIR):
    if not folder_name.endswith("_crop"):
        continue

    folder_path = os.path.join(PDF_ROOT_DIR, folder_name)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)

            # 🔄 구강_구내염.pdf → 구강_구내염.json
            base_name = os.path.splitext(filename)[0]
            output_json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

            print(f"📄 처리 중: {pdf_path}")
            try:
                call_document_parse_text_only(pdf_path, output_json_path)
            except Exception as e:
                print(f"❌ 예외 발생: {e}")