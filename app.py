import streamlit as st
from llm_api import ask_disease_recommendation, ask_doctor_info

st.set_page_config(page_title="PreMedix Chatbot", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [
        ("bot", "서울 보라매병원입니다. 안녕하세요! 어떤 증상이 있으신지 자세히 알려주세요!")
    ]
    st.session_state.selected_disease = None
    st.session_state.doctors = []

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
        chat_bubble("가장 가까운 질병을 버튼으로 선택해주세요.", sender="bot")
        cols = st.columns(len(msg))
        for i, label in enumerate(msg):
            if cols[i].button(f"✅ {label}"):
                st.session_state.selected_disease = label
                st.session_state.messages.append(("user", label))

                # LangChain으로 의사 정보 요청
                response = ask_doctor_info(label)
                st.session_state.messages.append(("bot", response["message"]))
                for doc in response["doctors"]:
                    doc_msg = f"""👨‍⚕️ <b style='color:#007BFF;'>{doc['name']}</b> 
                    <span style='color:gray;'>({doc['department']})</span><br>
                    <b>전문 분야:</b> {doc['specialty']}"""
                    st.session_state.messages.append(("bot", doc_msg))
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
    response = ask_disease_recommendation(user_input)
    st.session_state.messages.append(("bot", response["message"]))
    st.session_state.messages.append(("interactive", response["choices"]))
    st.rerun()
