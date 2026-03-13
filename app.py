import streamlit as st
import ccxt
import requests
import pandas as pd
from datetime import datetime

# 🔐 1. 비밀 금고(Secrets) 정보 가져오기
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    st.warning("⚠️ 스트림릿 Secrets 설정을 확인해주세요.")

# 📢 2. 텔레그램 무전 함수
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.get(url, params=params)
    except:
        pass

# 🌟 3. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🔑 4. 회원 시스템 (세션 상태 초기화)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 사이드바 ---
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src="https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png" width="130">
        <h2 style='color: #26A17B;'>USDT AI TRADER</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    if st.session_state['logged_in']:
        st.success(f"⚓ {st.session_state['user_id']}님 환영합니다!")
        if st.button("🔔 무전기 테스트"):
            send_telegram_msg("⚓ 아르 아빠님! AI 시스템에 정상 접속되었습니다. 감시를 시작합니다!")
            st.toast("텔레그램 확인!")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- 메인 화면 ---
if not st.session_state['logged_in']:
    st.subheader("🔐 시스템 접속")
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("아이디", value="admin")
        user_pw = st.text_input("비밀번호", type="password")
        if st.button("AI 시스템 접속"):
            # 임시 관리자 계정: admin / aror737
            if user_id == "admin" and user_pw == "aror737":
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
else:
    st.title("📈 실시간 김프 감시 대시보드")
    st.info("현재 유닛 737이 24시간 김프를 감시하고 있습니다.")
    
    # 여기에 실제 김프 계산 코드를 다음 단계에서 넣을 거예요!
    st.metric(label="현재 예상 김프", value="1.2%", delta="-0.2%")
    st.write("설정하신 알림 기준(1.0%) 보다 낮아지면 자동으로 무전을 보냅니다.")
