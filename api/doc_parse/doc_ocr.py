# pip install requests
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
filename = "../../pdf_samples/구강_구강건조증.pdf"

# 출력 파일명 자동 설정
input_path = Path(filename)
output_dir = Path("../output")
output_dir.mkdir(parents=True, exist_ok=True)
base_name = input_path.stem  # "구강_구강건조증"
json_path = output_dir / f"{base_name}_ocr.json"
txt_path = output_dir / f"{base_name}_ocr.txt"

# API 호출
url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {API_KEY}"}

files = {
    "document": open(filename, "rb"),
    "model": (None, "ocr")  # 확실하게 명시
}

response = requests.post(url, headers=headers, files=files)

# 응답 처리
if response.status_code == 200:
    result = response.json()

    # JSON 저장
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, ensure_ascii=False, indent=2)

    # OCR 텍스트만 추출
    if "text" in result:
        with open(txt_path, "w", encoding="utf-8") as f_txt:
            f_txt.write(result["text"])
        print(f"✅ OCR 텍스트 저장 완료: {txt_path}")
    else:
        print("⚠️ 'text' 필드가 응답에 없습니다. 구조를 확인하세요.")
else:
    print(f"❌ API 오류 (status: {response.status_code})")
    print(response.text)
