import streamlit as st
#from llm_api import ask_disease_recommendation, ask_doctor_info
from main2 import get_disease_and_doctors

st.set_page_config(page_title="PreMedix Chatbot", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [
        ("bot", "서울 보라매병원입니다. 안녕하세요! 어떤 증상이 있으신지 자세히 알려주세요!")
    ]
    st.session_state.selected_disease = None
    st.session_state.doctors = []

    st.session_state.last_response = None # 마지막 응답 저장용

# 말풍선 출력 함수
def chat_bubble(text, sender="bot"):
    align = "left" if sender == "bot" else "right"
    color = "#f1f0f0" if sender == "bot" else "#d1e7dd"
    border_radius = "15px 15px 15px 0px" if sender == "bot" else "15px 15px 0px 15px"

    bubble = f"""
    <div style='display: flex; justify-content: {align}; margin: 10px 0;'>
        <div style='background: {color}; padding: 10px 15px; border-radius: {border_radius}; max-width: 75%;'>
            {text}
        </div>
    </div>
    """
    st.markdown(bubble, unsafe_allow_html=True)

# 버튼 hover 효과 CSS
st.markdown("""
<style>
button:hover {
    background-color: #d4f1f4 !important;
    color: #007BFF !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# 타이틀
st.markdown("<h2 style='text-align:center;'>🏥 PreMedix Chatbot</h2>", unsafe_allow_html=True)

# 메시지 출력
for sender, msg in st.session_state.messages:
    if sender in ["bot", "user"]:
        chat_bubble(msg, sender)
    elif sender == "interactive":
        chat_bubble("가장 가까운 질병을 선택해주세요.", sender="bot")
        disease_cols = st.columns(len(msg) + 1)
        for i, disease in enumerate(msg):  # msg는 disease_candidates 리스트
            name = disease["name"]

            if disease_cols[i].button(f"✅ {name}"):
                st.session_state.selected_disease = disease
                st.session_state.messages.append(("user", name))

                doctor_info = st.session_state.last_response["doctors_by_disease"].get(name)
                if doctor_info:
                    st.session_state.messages.append(("bot", doctor_info["message"]))
                    for doc in doctor_info["doctors"]:
                        doc_msg = f"""👨‍⚕️ <b style='color:#007BFF;'>{doc['name']} 교수</b> 
                        <span style='color:gray;'>({doc['department']})</span><br>
                        <b>전문 분야:</b> {doc['specialty']}"""
                        st.session_state.messages.append(("bot", doc_msg))
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 아무 것도 해당하지 않아요"):
            st.session_state.messages.append(("user", "아무 것도 해당하지 않아요"))
            msg = "\U0001F3E5 보다 정확한 진단과 처치를 위해 방문 접수 하시거나,\n\U0001F4DE 전화 상담을 통해 전문적인 안내를 받아보시길 권해드립니다."

            st.session_state.messages.append(("bot", msg ))
            st.rerun()
# 입력창
st.markdown("---")
with st.form("chat_input", clear_on_submit=True):
    cols = st.columns([10, 1])
    user_input = cols[0].text_input("메시지를 입력하세요", label_visibility="collapsed")
    submitted = cols[1].form_submit_button("✉️", use_container_width=True)

if submitted and user_input:
    st.session_state.messages.append(("user", user_input))

    # LangChain으로 질병 추천 요청
    response = get_disease_and_doctors(user_input)

    st.session_state.last_response = response
    
    st.session_state.messages.append((
        "bot",
        f"다음은 '{response['symptom']}'에 대한 가능성 있는 질병들입니다:\n\n" +
        "\n".join(
            [f"{i+1}. **{d['name']}** : {d['description']}" for i, d in enumerate(response["disease_candidates"])]
        )
    ))
    st.session_state.messages.append(("interactive", response["disease_candidates"]))
    st.rerun()
