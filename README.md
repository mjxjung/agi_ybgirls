# agi_ybgirls

1. Database/diseaseinfo에 crawling pdf 저장되어있음
2. doc_parsing api를 통해 -> Database/info에 api 처리된 파일 저장되어있음
3. api/crop_parsing 폴더의 전처리를 통해 -> Database/output/processed_final에 전처리 완료된 파일 저장되어있음

### 가상환경 실행(선택)
0. python3 -m venv agi_ybgirls
1. source agi_ybgirls/bin/activate
2. pip install -r requirements.txt
3. deactivate

### 크롤링 처리 방법
- (pip freeze > requirements.txt)
1. pip install -r requirements.txt
2. python Crawling/diseaseinfo_crop.py
3. 손수 폴더로 옮겨 담으슈

### Upstage parsing Api 일괄 사용 및 전처리
1. .env 파일 설정
2. python api/doc_parse/doc_parsing.py실행
3. parsing data 전처리
4. python api/crop_parsing/parsing.py
