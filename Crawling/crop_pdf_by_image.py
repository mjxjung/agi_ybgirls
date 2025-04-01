import os
import fitz  # PyMuPDF
from PIL import Image

# 경로 설정
SOURCE_DIR = "Database/diseaseinfo"

# 크롭할 픽셀 설정
LEFT_CROP = 500
TOP_CROP = 100

# PDF 첫 페이지만 크롭 이미지로 교체하고 나머지는 그대로 복사
def crop_first_page_only(input_path, output_path):
    try:
        doc = fitz.open(input_path)

        # 1️⃣ 첫 페이지 처리
        page = doc.load_page(0)
        pix = page.get_pixmap()
        temp_img_path = output_path.replace(".pdf", "_page1.png")
        pix.save(temp_img_path)

        img = Image.open(temp_img_path)
        width, height = img.size
        cropped_img = img.crop((LEFT_CROP, TOP_CROP, width, height))
        cropped_pdf_path = output_path.replace(".pdf", "_page1.pdf")
        cropped_img.save(cropped_pdf_path, "PDF")
        os.remove(temp_img_path)

        # 2️⃣ 나머지 페이지 복사
        new_doc = fitz.open()

        # 첫 페이지 (크롭된 이미지 PDF)
        first_page_doc = fitz.open(cropped_pdf_path)
        new_doc.insert_pdf(first_page_doc)
        first_page_doc.close()
        os.remove(cropped_pdf_path)

        # 원본 PDF의 나머지 페이지들 추가
        if len(doc) > 1:
            new_doc.insert_pdf(doc, from_page=1)

        new_doc.save(output_path)
        new_doc.close()
        doc.close()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# 하위 디렉토리 탐색 및 처리
for subdir in os.listdir(SOURCE_DIR):
    subdir_path = os.path.join(SOURCE_DIR, subdir)
    if os.path.isdir(subdir_path):
        target_subdir = f"{subdir_path}_crop"
        os.makedirs(target_subdir, exist_ok=True)

        for filename in os.listdir(subdir_path):
            if filename.lower().endswith(".pdf"):
                input_pdf_path = os.path.join(subdir_path, filename)
                output_pdf_path = os.path.join(target_subdir, filename)

                print(f"🔄 첫 페이지만 크롭, 나머지는 유지: {input_pdf_path}")
                crop_first_page_only(input_pdf_path, output_pdf_path)
                print(f"✅ 저장 완료: {output_pdf_path}")

print("🎉 모든 PDF 파일 첫 페이지만 크롭하여 저장 완료되었습니다.")