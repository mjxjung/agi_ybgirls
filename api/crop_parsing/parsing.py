# parsing.py

import os
from extractor import extract_disease_name, extract_sections, save_chunks_to_file, process_sections
from loader import load_json


def run_parsing_pipeline(input_json_path: str, output_dir: str, final_output_dir: str):
    """
    단일 파일 처리 파이프라인
    """
    try:
        # 1. 데이터 로드
        data = load_json(input_json_path)

        # 2. 병명 추출
        html = data['content']['html']
        disease_name = extract_disease_name(html)
        print(f"\n📌 파일: {input_json_path} | 병명: {disease_name}")

        # 3. 섹션 추출
        chunks = extract_sections(data, disease_name)
        print(f"  🔹 섹션 수: {len(chunks)}")

        # 4. 1차 저장
        save_chunks_to_file(chunks, output_dir, disease_name)

        # 5. 후처리 (Q/A 분리 등)
        processed_chunks = process_sections(chunks)
        save_chunks_to_file(processed_chunks, final_output_dir, disease_name)

    except Exception as e:
        print(f"❌ 에러 발생 - 파일: {input_json_path}\n{e}")


def run_batch_parsing(input_dir: str, output_dir: str, final_output_dir: str):
    """
    폴더 내 모든 .json 파일에 대해 파이프라인 실행
    """
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    if not json_files:
        print("❌ 처리할 JSON 파일이 없습니다.")
        return

    print(f"📁 총 {len(json_files)}개 파일 처리 시작...")

    for file_name in json_files:
        input_path = os.path.join(input_dir, file_name)
        run_parsing_pipeline(input_path, output_dir, final_output_dir)


if __name__ == "__main__":
    # ✅ 사용자 지정 경로
    input_folder = "Database/input/"                      # 👉 여기에 처리할 JSON 파일 폴더 넣기
    output_folder = "Database/output/processed/"         # 👉 1차 저장 위치
    final_output_folder = "Database/output/processed_final/"       # 👉 후처리 저장 위치

    run_batch_parsing(input_folder, output_folder, final_output_folder)