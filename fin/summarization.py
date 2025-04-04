from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI

import os
import json

def summarize_symptoms(disease_symptoms):
    """
    환자가 준 환자의 증상 정보만 요약
    """
    docs = [Document(page_content=disease_symptoms)]
    model = ChatOpenAI(model="gpt-4o-mini")
    chain = load_summarize_chain(model, chain_type="map_reduce")
    summary = chain.invoke(docs)
    return summary

def summarize_disease_symptoms(json_folder, disease_name):
    """
    주어진 폴더 내의 JSON 파일에서, disease_name과 일치하는 disease 필드를 가진 항목 중
    section이 '개요' 또는 '증상'인 경우의 'content' 텍스트를 전부 이어 붙여서
    2~3문장 정도로 간단히 요약을 수행합니다.
    """

    # (1) disease_name에 해당하는 "개요", "증상" 텍스트 모으기
    disease_texts = []
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            json_path = os.path.join(json_folder, filename)
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # JSON 파싱 오류 시 건너뜀
                    continue

                # 파일 내용이 list 형태인지 확인
                if isinstance(data, list):
                    for entry in data:
                        if entry.get("disease") == disease_name:
                            section = entry.get("section")
                            # 개요나 증상이면 content 모으기
                            if section in ["개요", "증상"]:
                                content = entry.get("content", "")
                                disease_texts.append(content)
                # 데이터 구조가 list가 아닐 경우 무시

    # (2) 여러 텍스트를 하나로 합치기
    if not disease_texts:
        return f"해당 질병({disease_name})에 대한 '개요' 또는 '증상' 데이터가 없습니다."

    combined_text = "\n\n".join(disease_texts)

    # (3) Document 객체 생성
    doc = Document(page_content=combined_text)

    # (4) 사용자 정의 프롬프트
    # 이번에는 'map_reduce' 체인을 사용하는 예시를 보여드립니다.
    # 이 체인은 'map' 단계와 'combine' 단계를 위해 서로 다른 프롬프트가 필요합니다.
    map_prompt_template = """아래 텍스트를 간단히 요약해 주세요:

{text}
"""
    combine_prompt_template = """아래 부분 요약들을 종합해서,
2~3문장 정도의 간단한 최종 요약문을 작성해 주세요. '~입니다, ~합니다' 형태의 친절한 어조를 사용하세요.

{text}
"""
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

    # (5) 요약 체인 실행
    # gpt-4o-mini 모델명을 예시로 사용
    model = CommunityChatOpenAI(model_name="gpt-4o-mini")

    chain = load_summarize_chain(
        llm=model,
        chain_type="map_reduce",
        map_prompt=map_prompt,          # map 단계 프롬프트
        combine_prompt=combine_prompt,  # combine 단계 프롬프트
        memory=None                     # 대화 메모리 미사용
    )

    # map_reduce 체인은 여러 문서가 들어가면 각각 요약 후 종합하므로,
    # doc 하나만 넣더라도 내부적으로 map->reduce 과정을 거칩니다.
    summary = chain.run([doc])

    return summary
