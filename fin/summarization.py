from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI

def summarize_symptoms(disease_symptoms, recommended_disease):
    docs = [Document(page_content=disease_symptoms)]
    model = ChatOpenAI(model="gpt-4o")
    chain = load_summarize_chain(model, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary
