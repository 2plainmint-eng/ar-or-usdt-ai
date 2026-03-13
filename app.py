import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보 가져오기
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

# 💰 3. 데이터 낚시 장비 (환율 + 업비트)
def get_kimp_data():
    try:
        # 업비트 가격
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        # 실시간 환율 (미끼 강화)
        ex_url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        ex_res = requests.get(ex_url, headers=headers, timeout=5).json()
        ex_rate = float(ex_res[0]['basePrice'])
        
        kimp = ((up_price / ex_rate) - 1) * 100
        return up_price, ex_rate, kimp
    except:
        return None, None, None

# 🌟 4. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🛠️ [중요] 5. 에러 방지용 초기 이름표 설정 (여기서 에러를 잡습니다!)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = "Guest"

# --- 사이드바 ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='100'></div>", unsafe_allow_html=True)
    st.title("USDT 감시단")
    st.write("---")
    
    # 로그인 상태일 때만 보이는 메뉴
    if st.session_state['logged_in']:
        # .get()을 써서 이름표가 없어도 에러가 안 나게 한 번 더 방어!
        u_id = st.session_state.get('user_id', '관리자')
        st.success(f"⚓ {u_id}님 항해 중")
        
        if st.button("🔔 무전기 테스트"):
            send_telegram_msg(f"⚓ {u_id}님! AI 시스템이 정상 작동 중입니다!")
            st.toast("무전 완료!")
            
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- 메인 화면 ---
if not st.session_state['logged_in']:
    st.subheader("🔐 시스템 접속")
    input_id = st.text_input("아이디", value="admin")
    input_pw = st.text_input("비밀번호", type="password")
    
    if st.button("AI 시스템 접속"):
        if input_id == "admin" and input_pw == "aror737":
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = input_id # 여기서 이름표를 확정!
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
else:
    st.title("📈 실시간 김프 현황")
    
    # 데이터 가져오기
    u_price, ex_rate, kimp_val = get_kimp_data()
    
    if u_price and ex_rate:
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("실시간 환율", f"{ex_rate:,.1f} 원")
        
        # 김프 색상 (1% 기준)
        k_color = "normal" if kimp_val > 1.0 else "inverse"
        c3.metric("실시간 김프", f"{kimp_val:.2f} %", delta=f"{kimp_val-1.0:.2f}%", delta_color=k_color)
        
        st.write("---")
        st.caption(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
        
        # 10초 자동 새로고침
        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 데이터를 낚는 중입니다... 잠시만 기다려주세요.")
        time.sleep(3)
        st.rerun()
