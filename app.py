import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 📢 2. 텔레그램 무전 함수
def send_telegram_msg(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.get(url, params=params, timeout=5)
        except: pass

# 💰 3. 실시간 가격 및 김프 계산 (더 튼튼한 낚시대)
def get_kimp_data():
    try:
        # 업비트 가격 (시장가)
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        # 환율 가져오기 (방법 1: 두나무 직접 / 안되면 방법 2: 다른 곳)
        headers = {'User-Agent': 'Mozilla/5.0'}
        ex_url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
        ex_res = requests.get(ex_url, headers=headers, timeout=5).json()
        ex_rate = float(ex_res[0]['basePrice'])
        
        kimp = ((up_price / ex_rate) - 1) * 100
        return up_price, ex_rate, kimp
    except Exception as e:
        # 무엇이 문제인지 사이드바에 비밀스럽게 표시
        st.sidebar.warning(f"🔍 낚시 실패 이유: {str(e)}")
        return None, None, None

# 🌟 4. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🛠️ 5. 세션 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = "Guest"

# --- 사이드바 ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='100'></div>", unsafe_allow_html=True)
    st.title("USDT 감시단")
    st.write("---")
    
    if st.session_state['logged_in']:
        st.success(f"⚓ {st.session_state['user_id']}님 항해 중")
        if st.button("🔔 무전 테스트"):
            send_telegram_msg("⚓ 아빠님! 무전기가 정상입니다!")
            st.toast("무전 완료!")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- 메인 화면 로직 ---
# 로그인이 안 되어 있으면 무전기/낚시 로직을 아예 실행 안 함!
if not st.session_state['logged_in']:
    st.title("🛡️ AI 보안 시스템")
    st.write("시스템에 접속하려면 비밀번호를 입력하세요.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        input_id = st.text_input("아이디", value="admin")
        input_pw = st.text_input("비밀번호", type="password")
        
        if st.button("AI 시스템 접속"):
            if input_id == "admin" and input_pw == "aror737":
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = input_id
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
else:
    # 로그인 성공 시에만 데이터를 낚아오기 시작!
    st.title("📈 실시간 김프 현황")
    
    with st.spinner("🎣 유닛 737이 바다 깊은 곳에서 데이터를 낚는 중..."):
        u_price, ex_rate, kimp_val = get_kimp_data()
    
    if u_price and ex_rate:
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("실시간 환율", f"{ex_rate:,.1f} 원")
        
        # 김프 색상
        k_color = "normal" if kimp_val > 1.0 else "inverse"
        c3.metric("실시간 김프", f"{kimp_val:.2f} %", delta=f"{kimp_val-1.0:.2f}%", delta_color=k_color)
        
        st.write("---")
        st.caption(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
        
        time.sleep(10)
        st.rerun()
    else:
        st.error("⚠️ 현재 데이터 낚시가 지연되고 있습니다.")
        st.info("사이드바의 '디버깅' 정보를 확인하거나 잠시만 기다려주세요.")
        time.sleep(5)
        st.rerun()
