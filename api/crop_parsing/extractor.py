# extractor.py

import re
from bs4 import BeautifulSoup
import os
import json
import pandas as pd
from datetime import datetime


def extract_disease_name(html: str) -> str:
    """
    HTML 문자열에서 병명을 추출하는 함수

    1. <h1> 태그에서 추출
    2. <p> 또는 <header> 태그 중 style="font-size:22px"에서 추출
    3. '• 콘텐츠명 :' 포함된 문장에서 추출

    Args:
        html (str): HTML 문자열

    Returns:
        str: 추출된 병명 (없으면 'Unknown Disease')
    """
    soup = BeautifulSoup(html, 'html.parser')
    disease_name = ""

    # 1. <h1> 태그에서 추출
    disease_tag = soup.find("h1")

    # 2. h1 태그 없을 경우, font-size:22px 스타일이 있는 <p> 또는 <header>에서 추출
    if disease_tag is None:
        for tag in soup.find_all(["p", "header"]):
            style = tag.get("style", "")
            if "font-size:22px" in style:
                disease_tag = tag
                break

    # 3. 최종적으로 병명 추출
    if disease_tag:
        disease_name = disease_tag.get_text(strip=True)

    # 4. 그래도 추출 실패 시, '• 콘텐츠명 :' 포함된 문장에서 추출
    if not disease_name:
        for tag in soup.find_all("p"):
            text = tag.get_text(strip=True)
            if "• 콘텐츠명" in text:
                match = re.search(r"콘텐츠명\s*:\s*(.+)", text)
                if match:
                    disease_name = match.group(1).strip()
                    break

    return disease_name or "Unknown Disease"


def extract_sections(data: dict, disease_name: str) -> list[dict]:
    """
    문서 data에서 섹션별 내용을 추출하는 함수

    Args:
        data (dict): notebook에서 불러온 JSON 데이터
        disease_name (str): 추출된 병명

    Returns:
        list[dict]: 섹션별로 나눈 병명, 제목, 본문, 페이지 정보를 담은 리스트
    """
    # 기본 설정
    MAX_HEADING_LENGTH = 20
    first_page_font_threshold = 22
    other_page_font_threshold = 18

    chunks = []
    current_section = None
    current_text = []
    current_page = None

    for elem in data.get('elements', []):
        html = elem.get("content", {}).get("html", "")
        text = BeautifulSoup(html, "html.parser").get_text(strip=True)
        page = elem.get("page", 1)
        category = elem.get("category", "")
        style = ""

        # 스타일에서 font-size 추출
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find()
        if tag:
            style = tag.get("style", "")
        
        font_size = 0
        if "font-size:" in style:
            try:
                font_size = int(style.split("font-size:")[1].replace("px", "").strip())
            except:
                pass

        # heading 조건
        threshold = first_page_font_threshold if page == 1 else other_page_font_threshold
        is_heading = (
            (category.startswith("heading") or font_size >= threshold)
            and len(text) <= MAX_HEADING_LENGTH
        )

        if not text:
            continue

        # ✅ 그림 처리 예외
        if text.startswith("<그림") and ">" in text:
            match = re.match(r"<(.*?)>(.*)", text)
            if match:
                fig_section = match.group(1).strip()
                fig_content = match.group(2).strip()
                chunks.append({
                    "disease": disease_name,
                    "section": fig_section,
                    "content": fig_content,
                    "page": page
                })
            continue

        if is_heading:
            if current_section and current_text:
                chunks.append({
                    "disease": disease_name,
                    "section": current_section,
                    "content": "\n".join(current_text).strip(),
                    "page": current_page
                })
                current_text = []

            current_section = text
            current_page = page
        else:
            current_text.append(text)

    # 마지막 섹션 저장
    if current_section and current_text:
        chunks.append({
            "disease": disease_name,
            "section": current_section,
            "content": "\n".join(current_text).strip(),
            "page": current_page
        })

        return chunks


def save_chunks_to_file(chunks: list[dict], folder_path: str, disease_name: str) -> None:
    """
    폴더 경로를 입력받아 chunks를 JSON과 CSV로 저장하는 함수.

    Parameters:
        chunks (list[dict]): 섹션별로 분류된 텍스트 데이터
        folder_path (str): 저장할 폴더 경로
        disease_name (str): 병명 (파일명으로 사용됨)
    """
    # 폴더 없으면 생성
    os.makedirs(folder_path, exist_ok=True)

    # 병명에 들어갈 수 없는 문자 제거
    safe_disease_name = "".join(c for c in disease_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")

    # 타임스탬프 (optional, 이름 충돌 방지용)
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 저장 경로 지정
    json_path = os.path.join(folder_path, f"{safe_disease_name}.json")
    # csv_path = os.path.join(folder_path, f"{safe_disease_name}.csv")

    # 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    # pd.DataFrame(chunks).to_csv(csv_path, index=False)

    print(f"✅ JSON 저장 완료: {json_path}")
    # print(f"✅ CSV 저장 완료: {csv_path}")


def process_sections(chunks: list[dict]) -> list[dict]:
    """
    저장된 섹션 데이터를 후처리하는 함수
    - 질병명과 같은 제목 제거
    - 공공누리 문구 제거
    - '자주하는 질문' 섹션을 Q/A 쌍으로 분리
    - 섹션명이 '그림'으로 시작하면 제외
    - 본문에 (그림...) 형태가 있으면 삭제
    - 특정 불필요 문구 제거
    - 요약문이 등록일자일 경우 제거

    Parameters:
        chunks (list[dict]): 저장된 섹션 정보 리스트

    Returns:
        list[dict]: 후처리된 섹션 리스트
    """

    def split_qa_section(disease, content, page):
        qa_chunks = []

        # 줄 기준으로 자르기
        lines = content.splitlines()

        question = None
        answer_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("Q."):
                # 이전 QA 쌍 저장
                if question and answer_lines:
                    qa_chunks.append({
                        "disease": disease,
                        "section": question,
                        "content": "\n".join(answer_lines).strip(),
                        "page": page
                    })
                    answer_lines = []

                question = line

            elif line.startswith("A") or line.startswith("A."):
                # A 라인 자체는 저장하지 않고, 다음 줄부터 answer 시작
                continue

            elif question:
                answer_lines.append(line)

        # 마지막 QA 쌍 저장
        if question and answer_lines:
            qa_chunks.append({
                "disease": disease,
                "section": question,
                "content": "\n".join(answer_lines).strip(),
                "page": page
            })

        return qa_chunks

    REMOVE_SECTIONS = {
        '본 공공저작물은 공공누리 "출처표시+상업적이용금지+변경금지" 조건에 따라 이용할 수 있습니다.',
        "개인정보처리방침 개인정보이용안내 저작권정책 및 웹접근성",
        "※ 본 페이지에서 제공하는 내용은 참고사항일 뿐 게시물에 대한 법적책임은 없음을 밝혀드립니다. 자세한 내용은 전문가와 상담하시기 바랍니다.",
        "[ 28159 ] 충청북도 청주시 흥덕구 오송읍 오송생명2로 187 오송보건의료행정타운 내 질병관리청문의사항: 02-2030-6602 (평일 9:00-17:00, 12:00-13:00 제외) / 관리자 이메일 : nhis@korea.kr",
        "참고문헌"
    }

    new_chunks = []

    for chunk in chunks:
        disease = chunk["disease"]
        section = chunk["section"].strip()
        content = chunk["content"].strip()

        # ❌ 제거 조건
        if (
            section == disease or
            section.startswith("그림") or
            section in REMOVE_SECTIONS or
            (section == "요약문" and content.startswith("등록일자"))
        ):
            continue

        # ✅ 본문에서 (그림...) 형태 제거
        cleaned_content = re.sub(r"\(그림[^\)]*\)", "", content).strip()

        # 🔄 자주하는 질문 → Q/A 분리
        if section == "자주하는 질문":
            qa_split = split_qa_section(
                disease=disease,
                content=cleaned_content,
                page=chunk.get("page", 1)
            )
            new_chunks.extend(qa_split)
        else:
            new_chunks.append({
                "disease": disease,
                "section": section,
                "content": cleaned_content,
                "page": chunk.get("page", 1)
            })

    return new_chunks