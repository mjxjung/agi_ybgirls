# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document

# 1. JSON 파일 읽기 → Document 리스트로 변환
def load_json_documents(json_folder_path):
    documents = []
    for filename in os.listdir(json_folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(json_folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    content = item.get("content", "")
                    metadata = {
                        "disease": item.get("disease", ""),
                        "section": item.get("section", ""),
                        "page": item.get("page", "")
                    }
                    documents.append(Document(page_content=content, metadata=metadata))
    return documents

# 경로 설정
json_path = "disease_data"
 # 여기에 JSON 파일 여러 개가 들어 있는 폴더 경로를 넣으세요.

# 2. 문서 로드
docs = load_json_documents(json_path)

# 3. 문서 분할
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

# 4. 임베딩 및 벡터스토어 생성
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(split_docs, embeddings)

# 5. 검색기
retriever = vectorstore.as_retriever()

# 6. 프롬프트 정의
prompt = PromptTemplate.from_template(
    """너는 질병 정보를 바탕으로 질문에 대답하는 도우미야.
아래의 context를 참고해서 질문에 답해줘. 모르면 모른다고 말해.
반드시 한국어로 답변해줘.

질문: {question}

정보:
{context}

답변:"""
)

# 7. LLM 설정
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# 8. 체인 구성
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 9. 테스트
while True:
    question = input("질문을 입력하세요 (종료하려면 'exit'): ")
    if question.lower() == "exit":
        break
    answer = chain.invoke(question)
    print("\n📘 답변:\n", answer)
