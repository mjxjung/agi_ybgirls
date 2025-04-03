import fitz  # PyMuPDF
import json
from pathlib import Path

def extract_section_titles(pdf_path):
    """
    PDF 내 텍스트에서 섹션 제목을 추출합니다.
    제목 후보는 주요 키워드로 시작하는 줄을 기반으로 합니다.
    """
    doc = fitz.open(pdf_path)
    section_titles = set()

    # 문서 내에서 자주 등장하는 구조화 키워드 기반
    section_keywords = (
        "개요", "개요-정의", "개요-종류", "개요-원인", "개요-경과 및 예후", "개요-병태생리",
        "역학 및 통계", "증상", "진단 및 검사", 
        "치료", "치료-약물 치료", "치료-비약물 치료", "자가관리", 
        "위험요인 및 예방", "정기 진찰"
    )

    for page in doc:
        lines = page.get_text().split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            for keyword in section_keywords:
                if stripped.startswith(keyword):
                    section_titles.add(keyword)
                    break

    return sorted(section_titles)

def convert_to_upstage_schema(section_titles):
    """
    Upstage API에서 사용하는 json_schema 포맷에 맞게 변환
    """
    schema = {
        "name": "document_schema",
        "schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    # 기본 항목 (필요시 여기서 추가 가능)
    schema["schema"]["properties"]["title"] = {
        "type": "string",
        "description": "The title of the health information document."
    }
    schema["schema"]["properties"]["overview"] = {
        "type": "string",
        "description": "A brief overview of the health condition discussed in the document."
    }
    schema["schema"]["required"].extend(["title", "overview"])

    # 사용자 정의 섹션들 반영
    for section in section_titles:
        schema["schema"]["properties"][section] = {
            "type": "string",
            "description": f"{section}에 대한 내용입니다."
        }
        schema["schema"]["required"].append(section)

    return schema

def generate_upstage_response_format(pdf_path, output_path="response_format.json"):
    titles = extract_section_titles(pdf_path)
    upstage_schema = convert_to_upstage_schema(titles)

    full_response_format = {
        "type": "json_schema",
        "json_schema": upstage_schema
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_response_format, f, ensure_ascii=False, indent=2)

    print(f"✅ Upstage API response_format 저장 완료: {output_path}")
    return full_response_format


# 테스트 실행
if __name__ == "__main__":
    pdf_file = "../../pdf_samples/구강_구강건조증.pdf"

    schema_1 = generate_upstage_response_format(pdf_file)
    print(json.dumps(schema_1, ensure_ascii=False, indent=2))

