import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보 (없어도 작동하게 안전하게!)
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

# 💰 3. 실시간 가격 및 김프 계산 (가장 튼튼한 방식)
def get_kimp_data():
    try:
        # 방법 A: 업비트 공식 API로 직접 찌르기
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        upbit_price = float(up_res[0]['trade_price'])
        
        # 방법 B: 환율 가져오기 (두나무 공식 우회로)
        ex_url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        ex_res = requests.get(ex_url, headers=headers, timeout=5).json()
        exchange_rate = float(ex_res[0]['basePrice'])
        
        kimp = ((upbit_price / exchange_rate) - 1) * 100
        return upbit_price, exchange_rate, kimp
    except Exception as e:
        # 어디서 에러가 났는지 사이드바에 몰래 표시 (범인 검거용)
        st.sidebar.write(f"🔍 디버깅: {str(e)}")
        return None, None, None

# 🌟 4. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🔑 5. 회원 시스템
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 사이드바 ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='100'></div>", unsafe_allow_html=True)
    st.title("USDT 감시단")
    
    if st.session_state['logged_in']:
        st.success(f"⚓ {st.session_state['user_id']}님")
        if st.button("🔔 무전기 테스트"):
            send_telegram_msg("⚓ 아르 아빠님! 무전기가 정상입니다!")
            st.toast("무전 완료!")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- 메인 화면 ---
if not st.session_state['logged_in']:
    st.subheader("🔐 시스템 접속")
    user_id = st.text_input("아이디", value="admin")
    user_pw = st.text_input("비밀번호", type="password")
    if st.button("AI 시스템 접속"):
        if user_id == "admin" and user_pw == "aror737":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("비밀번호를 확인해주세요.")
else:
    st.title("📈 실시간 김프 현황")
    
    # 데이터 가져오기 시도
    u_price, ex_rate, kimp_val = get_kimp_data()
    
    if u_price and ex_rate:
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("실시간 환율", f"{ex_rate:,.1f} 원")
        
        # 김프 색상 조절
        k_color = "normal" if kimp_val > 1.0 else "inverse"
        c3.metric("실시간 김프", f"{kimp_val:.2f} %", delta=f"{kimp_val-1.0:.2f}%", delta_color=k_color)
        
        st.write("---")
        st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
        
        # 10초 대기 후 새로고침
        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 바다 깊은 곳에서 데이터를 낚고 있습니다... (잠시만 기다려주세요)")
        time.sleep(3)
        st.rerun()
