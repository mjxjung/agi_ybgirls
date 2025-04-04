# agi_ybgirls
## 프로젝트 개요
간호사의 전화 업무 부담을 줄여주는, 본격적인 진료 이전에 만나는 RAG 기반 AI 의료 비서 서비스. 

## 설치 방법 및 사용 방법

### 파일 구조
1. Database/diseaseinfo에 crawling pdf 저장되어있음
2. api/doc_parse/doc_parsing.py에서 Upstage의 Document Parse Api를 활용해 -> Database/input에 api 처리된 파일 저장되어있음
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

### Upstage parsing Api 일괄 사용 및 전처리
1. .env 파일 설정
2. python api/doc_parse/doc_parsing.py실행
3. parsing data 전처리
4. python api/crop_parsing/parsing.py

### 전처리된 데이터를 임베딩 후 벡터를 csv 파일에 저장
1. python main.py

2. 

### 임베딩 후 유사 질병 저장 (rag)
0. pip install -r requirements.txt
1. python fin/main.py

### streamlit 실행
1. python -m streamlit run fin/app.py
