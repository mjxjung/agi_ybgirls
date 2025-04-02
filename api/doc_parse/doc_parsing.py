import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
PDF_PATH = "../../pdf_samples/구강_구개열_crop.pdf"
OUTPUT_JSON = "../output/구강_구개열_crop_parsing.json"
OUTPUT_TEXT = "../output/구강_구개열_crop_parsing.txt"

def call_document_parse_text_only(input_file, json_output_file, text_output_file):
    response = requests.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {API_KEY}"},
        data={"base64_encoding": "['figure']"},
        files={"document": open(input_file, "rb"), "model": (None, "document-parse")}
    )

    if response.status_code == 200:
        parsed = response.json()

        # JSON 저장 (선택)
        with open(json_output_file, "w", encoding="utf-8") as f_json:
            json.dump(parsed, f_json, ensure_ascii=False, indent=2)

        # 텍스트 추출
        full_text = ""
        for page in parsed.get("pages", []):
            page_text = page.get("html", "")
            full_text += page_text.strip() + "\n\n"

        with open(text_output_file, "w", encoding="utf-8") as f_text:
            f_text.write(full_text)

        print(f"✅ 텍스트 추출 완료: {text_output_file}")

    else:
        raise ValueError(f"[ERROR] status {response.status_code}: {response.text}")


# 실행
call_document_parse_text_only(PDF_PATH, OUTPUT_JSON, OUTPUT_TEXT)
