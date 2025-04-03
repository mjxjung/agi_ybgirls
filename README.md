# agi_ybgirls

1. pdf_samples에서 doc_ocr / doc_parse / doc_parsing or information_extraction -> output file
2. output에서 전처리해서 문단별로 분류

### 가상환경 실행
0. python3 -m venv agi_ybgirls
1. source agi_ybgirls/bin/activate
2. pip install -r requirements.txt
3. deactivate

### 크롤링 처리 방법
(pip freeze > requirements.txt)
2. pip install -r requirements.txt
3. python Crawling/diseaseinfo_crop.py
4. 손수 폴더로 옮겨 담으슈

### Upstage parsing Api 일괄 사용 및 전처리
1. .env 파일 설정
2. python api/doc_parse/doc_parsing.py실행
3. parsing data 전처리
4. python api/crop_parsing/parsing.py

