# agi_ybgirls

1. pdf_samples에서 doc_ocr / doc_parse / doc_parsing or information_extraction -> output file
2. output에서 전처리해서 문단별로 분류

### 가상환경 실행
1. source agi_ybgirls/bin/activate
2. pip install -r requirements.txt
3. deactivate

### Upstage parsing Api 일괄 사용
0. .env 파일 설정
1. python api/doc_parse/doc_parsing.py실행

### parsing data 전처리
1. python api/crop_parsing/parsing.py
