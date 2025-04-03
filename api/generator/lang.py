import os
import glob
import json
import pandas as pd
from transformers import pipeline
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate

##############################################
# 1. 데이터 로드: 질병 정보 JSON → Document 변환
##############################################
def load_disease_documents(json_path: str):
    """
    JSON 파일(또는 폴더 내 다수의 JSON 파일)에서 질병 정보를 로드하여,
    같은 질병명을 가진 항목들을 그룹화한 후 각 질병별로 하나의 Document로 결합합니다.
    
    각 항목은 다음과 같은 키를 가집니다:
      - "disease": 질병명
      - "section": 정보의 섹션 (예: 개요, 증상, 치료 등)
      - "content": 실제 텍스트 내용
      - "page": 페이지 번호 (정보 정렬에 활용)
    
    반환:
      - 각 질병에 대해 관련 정보를 결합한 Document 리스트.
        Document의 page_content에는 각 섹션명과 내용을 포함하며, 
        metadata에는 "disease"가 저장됩니다.
    """
    documents = []
    
    # 단일 파일인 경우 처리
    if not os.path.isdir(json_path):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"{json_path} 파일이 존재하지 않습니다.")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON 파일의 최상위 구조는 리스트여야 합니다.")
    else:
        raise NotImplementedError("현재는 단일 파일만 지원합니다.")
    
    # 질병별로 정보를 그룹화
    disease_groups = {}
    for item in data:
        disease = item.get("disease", "").strip()
        section = item.get("section", "").strip()
        content = item.get("content", "").strip()
        page = item.get("page", None)
        if disease and content:
            if disease not in disease_groups:
                disease_groups[disease] = []
            # 페이지 번호가 있을 경우 정렬 기준으로 활용 (없으면 0으로 처리)
            disease_groups[disease].append((page if page is not None else 0, section, content))
    
    # 각 질병별로 정보를 정렬(페이지 번호 기준) 및 결합
    for disease, items in disease_groups.items():
        # 페이지 번호 기준 정렬
        items.sort(key=lambda x: x[0])
        combined_text = ""
        for page, section, content in items:
            combined_text += f"[{section}]\n{content}\n\n"
        doc = Document(
            page_content=combined_text.strip(),
            metadata={"disease": disease}
        )
        documents.append(doc)
    
    return documents

##############################################
# 2. 데이터 로드: 의사 정보 CSV 로드
##############################################
def load_doctor_data(csv_path: str):
    """
    CSV 파일에서 질환별 매칭된 의사 정보를 로드.
    CSV 파일은 첫 번째 행에 "병명", "추천의사1", "추천의사2", "추천의사3" 칼럼으로 구성되어 있음.
    "추천의사1"은 반드시 채워져 있으며, "추천의사2"와 "추천의사3"는 없거나 비어있을 수 있음.
    
    반환:
      - 질병명을 key로 하고, 추천 의사 목록(리스트)을 value로 하는 딕셔너리.
      예:
         {
            "구강건조증": ["Dr. 박"],
            "감기": ["Dr. 이", "Dr. 김"]
         }
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} 파일이 존재하지 않습니다.")
        
    df = pd.read_csv(csv_path)
    
    doctor_mapping = {}
    for _, row in df.iterrows():
        disease = row.get("병명")
        recommended_doctors = []
        for col in ["추천의사1", "추천의사2", "추천의사3"]:
            if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                recommended_doctors.append(row[col])
        doctor_mapping[disease] = recommended_doctors
        
    return doctor_mapping

##############################################
# 3. 질병 정보 요약 함수
##############################################
def summarize_disease_info(text: str, summarizer) -> str:
    """
    질병 정보(예: 개요와 증상)를 LLM summarizer로 요약.
    """
    summary = summarizer(text, max_length=80, min_length=30, do_sample=False)
    return summary[0]['summary_text']

##############################################
# 4. 프롬프트 템플릿 정의
##############################################
# (1) 후보 질병 및 요약 제공 프롬프트 템플릿
prompt_template_candidates = PromptTemplate(
    template=(
        "환자의 증상: {query}\n\n"
        "아래 질병 정보들을 참고하여, 증상에 부합하는 상위 3개의 질병 후보를 제시하고, "
        "각 후보 질병에 대해 간략한 요약(개요와 주요 증상)을 작성해줘.\n\n"
        "질병 정보:\n{context}\n\n"
        "답변은 아래 형식으로 작성해줘:\n"
        "1. 후보 질병 1: [질병명]\n"
        "   - 요약: [개요와 주요 증상]\n\n"
        "2. 후보 질병 2: [질병명]\n"
        "   - 요약: [개요와 주요 증상]\n\n"
        "3. 후보 질병 3: [질병명]\n"
        "   - 요약: [개요와 주요 증상]\n\n"
        "각 후보 질병은 질병 정보와 증상 분석을 기반으로 선정해줘."
    ),
    input_variables=["query", "context"]
)

##############################################
# 5. 서비스 메인 흐름: 후보 질병 제안 및 추천 의사 제공
##############################################
def main():
    # 5-1. 데이터 로드
    disease_json_path = "disease_data"   # 질병 정보 JSON 파일(또는 폴더)
    doctor_csv_path = "doctor_info.csv"    # 의사 정보 CSV 파일

    try:
        disease_documents = load_disease_documents(disease_json_path)
        print("질병 정보 데이터 로드 성공!")
    except Exception as e:
        print("질병 데이터 로드 실패:", e)
        return

    try:
        doctor_mapping = load_doctor_data(doctor_csv_path)
        print("의사 정보 데이터 로드 성공!")
    except Exception as e:
        print("의사 데이터 로드 실패:", e)
        return

    # 5-2. 임베딩 모델과 FAISS 벡터스토어 생성
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(disease_documents, embeddings)
    # retrieval 시 상위 3개의 문서를 가져오도록 설정
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 5-3. LLM 및 Summarization 파이프라인 설정 (예시: GPT-2, Bart 기반 summarizer)
    generator_pipeline = pipeline("text-generation", model="gpt2", tokenizer="gpt2")
    llm = HuggingFacePipeline(pipeline=generator_pipeline)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer="facebook/bart-large-cnn")

    # 5-4. 후보 질병 제안을 위한 RetrievalQA 체인 생성 (프롬프트 템플릿: prompt_template_candidates)
    candidate_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template_candidates}
    )

    # 5-5. 사용자 입력: 증상 기반 질병 예측 요청
    user_query = input("증상을 입력해 주세요: ")  # 예: "입력이 요즘 구강의 건조함과 구취로 인해 불편함을 느낀다고 했어"
    print("\n[Step 1] 증상을 기반으로 후보 질병 3개와 요약 정보를 생성 중입니다...\n")
    
    # 5-6. 체인 실행: 후보 질병 및 요약 정보를 생성
    result_candidates = candidate_chain({"query": user_query})
    candidate_output = result_candidates.get("result", "")
    print("후보 질병 및 요약 정보:")
    print(candidate_output)
    
    # 5-7. 사용자가 후보 질병 중 하나 선택 (실제 서비스에서는 UI를 통해 선택)
    selected_disease = input("\n후보 질병 중 하나를 선택해 주세요 (질병명을 정확히 입력): ")
    
    # 5-8. CSV로부터 선택된 질병의 추천 의사 정보를 조회
    recommended_doctors = doctor_mapping.get(selected_disease)
    if recommended_doctors is None:
        doctor_output = f"선택하신 '{selected_disease}' 질병에 대한 추천 의사 정보가 없습니다."
    else:
        # 추천 의사 목록을 문자열로 구성 (여러 의사가 있을 경우 쉼표로 구분)
        doctor_output = f"선택하신 '{selected_disease}'에 대한 추천 의사: " + ", ".join(recommended_doctors)
    
    # 5-9. 최종 출력 구성
    final_output = (
        f"\n입력 증상: {user_query}\n\n"
        f"후보 질병 및 요약 정보:\n{candidate_output}\n\n"
        f"{doctor_output}"
    )
    
    print("\n최종 결과:")
    print(final_output)

if __name__ == "__main__":
    main()
