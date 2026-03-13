import streamlit as st
import requests
from datetime import datetime
import time
import pandas as pd

# 🔐 1. 비밀 금고 정보
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 💰 2. 데이터 낚시 함수
def get_kimp_data():
    try:
        # 업비트 가격
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        # 글로벌 환율
        ex_url = "https://api.exchangerate-api.com/v4/latest/USD"
        ex_res = requests.get(ex_url, timeout=5).json()
        ex_rate = float(ex_res['rates']['KRW'])
        
        kimp = ((up_price / ex_rate) - 1) * 100
        return up_price, ex_rate, kimp
    except:
        return None, None, None

# 🌟 3. 페이지 설정
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")

# 🛠️ 4. 시스템 상태 초기화 (로그인 & 데이터 기록)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'kimp_history' not in st.session_state:
    st.session_state['kimp_history'] = [] # 김프 기록 보관함

# --- 메인 로직 ---

if not st.session_state['logged_in']:
    st.title("🛡️ 아르아빠 AI 오두막 보안")
    col1, _ = st.columns([1, 1.5])
    with col1:
        st.markdown(f"<img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='80'>", unsafe_allow_html=True)
        input_pw = st.text_input("오두막 열쇠(비밀번호)", type="password")
        if st.button("오두막 입장"):
            if input_pw == "aror737":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("열쇠가 맞지 않습니다!")

else:
    # --- 로그인 성공 시 화면 ---
    st.title("📈 실시간 김프 감시 대시보드")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 환영합니다!")
        st.write("---")
        st.write("🐱 **Ar & Or**: '아빠, 지금이 기회냥?'")
        st.write("🤖 **Unit 737**: '데이터 분석 중...'")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

    # 데이터 가져오기
    u_price, ex_rate, k_val = get_kimp_data()
    
    if u_price and ex_rate:
        # 1. 상단 숫자 지표
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("글로벌 환율", f"{ex_rate:,.1f} 원")
        k_color = "normal" if k_val > 0 else "inverse"
        c3.metric("현재 김프", f"{k_val:.2f} %", delta=f"{k_val:.2f}%", delta_color=k_color)

        # 2. 📈 김프 흐름 그래프 (기록 업데이트)
        # 새로운 데이터를 기록에 추가 (최대 20개까지만 유지)
        now_time = datetime.now().strftime('%H:%M:%S')
        st.session_state['kimp_history'].append({"시간": now_time, "김프": k_val})
        if len(st.session_state['kimp_history']) > 20:
            st.session_state['kimp_history'].pop(0)
        
        # 그래프 그리기
        df = pd.DataFrame(st.session_state['kimp_history'])
        st.write("---")
        st.subheader("📊 김프 변화 추이 (최근 20회)")
        st.line_chart(df.set_index("시간"))

        st.caption(f"최근 갱신: {now_time} (10초 자동 갱신 중)")
        
        time.sleep(10)
        st.rerun()
    else:
        st.warning("🔄 유닛 737이 낚싯줄을 던지는 중입니다...")
        time.sleep(3)
        st.rerun()
