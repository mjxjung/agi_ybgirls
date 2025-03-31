import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
PDF_PATH = "../../pdf_samples/구강_구강건조증.pdf"
OUTPUT_TEXT = "../output/구강_구강건조증_hierarchical.txt"

def call_document_parse_hierarchical(input_file, output_text_file):
    response = requests.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {API_KEY}"},
        data={"base64_encoding": "['figure']", "model": "document-parse"},
        files={"document": open(input_file, "rb")}
    )

    print(f"📡 API 응답 상태: {response.status_code}")
    if response.status_code != 200:
        raise ValueError(f"[ERROR] status {response.status_code}: {response.text}")

    parsed = response.json()
    pages = parsed.get("pages", [])
    print(f"📄 파싱된 페이지 수: {len(pages)}")

    # 병명은 첫 title 블록에서
    blocks = [b for p in pages for b in p.get("text_blocks", [])]
    lines = []
    current_section = None
    current_subsection = None

    for block in blocks:
        btype = block.get("type")
        text = block.get("text", "").strip()
        hierarchy = block.get("hierarchy", None)

        if not text:
            continue

        if btype == "title":
            lines.append(f"# {text}\n")

        elif btype == "heading":
            if hierarchy == "h1":
                current_section = text
                lines.append(f"\n## {text}\n")
            elif hierarchy == "h2":
                current_subsection = text
                lines.append(f"\n### {text}\n")
            elif hierarchy == "h3":
                lines.append(f"\n#### {text}\n")
            else:
                lines.append(f"\n### {text}\n")

        elif btype in ("paragraph", "list-item"):
            lines.append(text)

    structured_text = "\n".join(lines)

    with open(output_text_file, "w", encoding="utf-8") as f_txt:
        f_txt.write(structured_text)

    print(f"✅ 계층적 텍스트 저장 완료: {output_text_file}")

# 실행
call_document_parse_hierarchical(PDF_PATH, OUTPUT_TEXT)
