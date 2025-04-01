import os
import subprocess

# 경로 설정
SOURCE_DIR = "Database/diseaseinfo"

# pdfCropMargins 설치 여부 확인
try:
    subprocess.run(["pdf-crop-margins", "-h"], stdout=subprocess.DEVNULL)
except FileNotFoundError:
    print("pdfCropMargins가 설치되지 않았습니다. 설치 후 다시 시도해주세요.")
    print("pip install pdfCropMargins")
    exit(1)

# 크롭할 픽셀 설정 (상단, 우측, 하단, 좌측)
TOP_CROP = 0
RIGHT_CROP = 0
BOTTOM_CROP = 0
LEFT_CROP = 300

# PDF 크롭 실행 함수
def crop_pdf(input_path, output_path):
    subprocess.run([
        "pdf-crop-margins", "-p", "0", "-ap4",
        str(TOP_CROP), str(RIGHT_CROP), str(BOTTOM_CROP), str(LEFT_CROP),
        input_path, "-o", output_path
    ])

# 하위 디렉토리 탐색 및 PDF 크롭
for subdir in os.listdir(SOURCE_DIR):
    subdir_path = os.path.join(SOURCE_DIR, subdir)
    if os.path.isdir(subdir_path):
        target_subdir = f"{subdir_path}_crop"
        os.makedirs(target_subdir, exist_ok=True)

        for filename in os.listdir(subdir_path):
            if filename.lower().endswith(".pdf"):
                input_pdf_path = os.path.join(subdir_path, filename)
                output_pdf_path = os.path.join(target_subdir, filename)

                print(f"🔄 크롭 진행 중: {input_pdf_path}")
                crop_pdf(input_pdf_path, output_pdf_path)
                print(f"✅ 크롭 완료: {output_pdf_path}")

print("🎉 모든 하위 폴더의 PDF 파일 크롭이 완료되었습니다.")