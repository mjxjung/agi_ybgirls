import streamlit as st

st.set_page_config(page_title="병원 도우미 챗봇", layout="centered")

# 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.selected_disease = None
    st.session_state.doctors = []

# 말풍선 출력 함수 (타이핑 애니메이션 포함)
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
# 챗봇 버튼 hover 애니메이션 적용
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

# 채팅창 출력
st.markdown("<h2 style='text-align:center;'>🏥 병원 도우미 챗봇</h2>", unsafe_allow_html=True)

# 메시지 출력 루프
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
                st.session_state.messages.append(("bot", f"'{label}'를 선택하셨군요! 아래는 관련 전문의를 안내드릴게요."))

                doctor_info = {
                    "염좌": [
                        {"name": "김정형", "department": "정형외과", "specialty": "관절 인대 손상, 스포츠 손상"},
                        {"name": "이근육", "department": "재활의학과", "specialty": "근육 재활, 물리치료"}
                    ],
                    "관절염": [
                        {"name": "박관절", "department": "류마티스내과", "specialty": "만성 관절염, 면역 질환"},
                        {"name": "최정형", "department": "정형외과", "specialty": "관절 치환, 재활"}
                    ],
                    "골절": [
                        {"name": "이골절", "department": "정형외과", "specialty": "골절 고정술, 골절 후 재활"},
                        {"name": "정뼈튼", "department": "외상외과", "specialty": "외상 골절 응급 수술"}
                    ]
                }
                for doc in doctor_info.get(label, []):
                    doc_msg = f"""👨‍⚕️ <b style='color:#007BFF;'>{doc['name']}</b> 
                    <span style='color:gray;'>({doc['department']})</span><br>
                    <b>전문 분야:</b> {doc['specialty']}"""
                    st.session_state.messages.append(("bot", doc_msg))
                st.rerun()

# 입력창 하단 고정
st.markdown("---")
with st.form("chat_input", clear_on_submit=True):
    cols = st.columns([10, 1])
    user_input = cols[0].text_input("메시지를 입력하세요", label_visibility="collapsed")
    submitted = cols[1].form_submit_button("✉️", use_container_width=True)

if submitted and user_input:
    st.session_state.messages.append(("user", user_input))
    if not st.session_state.selected_disease:
        msg = "입력하신 증상을 바탕으로 분석한 결과, 아래 질병들이 의심돼요:<br>"
        msg += "1. <b>염좌</b>: 관절 인대가 손상되어 붓고 통증이 나타나는 질병입니다.<br>"
        msg += "2. <b>관절염</b>: 관절에 염증이 생기고 뻣뻣한 느낌과 통증을 동반합니다.<br>"
        msg += "3. <b>골절</b>: 뼈가 부러져 심한 통증과 부종이 나타납니다.<br><br>"
        msg += "가장 가까운 질병을 버튼으로 선택해 주세요."
        st.session_state.messages.append(("bot", msg))
        st.session_state.messages.append(("interactive", ["염좌", "관절염", "골절"]))
    st.rerun()

# 초기 메시지 안내
if not st.session_state.messages:
    st.session_state.messages.append(("bot", "증상을 입력해 주세요. 예: 발목이 붓고 아파요"))
