import streamlit as st
import ccxt
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고(Secrets) 정보 가져오기
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 📢 2. 텔레그램 무전 함수
def send_telegram_msg(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.get(url, params=params)
        except:
            pass

# 💰 3. 실시간 가격 및 김프 계산 (더 튼튼해진 버전!)
def get_kimp_data():
    try:
        # 업비트 USDT 가격 (ccxt가 안될 때를 대비해 직접 호출)
        upbit_res = requests.get('https://api.upbit.com/v1/ticker?markets=KRW-USDT').json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        # 환율 가져오기 (사람인 척 속이는 '미끼' 추가)
        headers = {'User-Agent': 'Mozilla/5.0'}
        ex_res = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD', headers=headers).json()
        exchange_rate = float(ex_res[0]['basePrice'])
        
        # 김프 계산
        kimp = ((upbit_price / exchange_rate) - 1) * 100
        
        return upbit_price, exchange_rate, kimp
    except Exception as e:
        # 에러가 나면 화면에 살짝 표시 (나중에 지워도 됨)
        # st.sidebar.error(f"오류 발생: {e}")
        return None, None, None

# 🌟 4. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🔑 5. 회원 시스템
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
        st.success(f"⚓ {st.session_state['user_id']}님 접속 중")
        if st.button("🔔 무전기 테스트"):
            send_telegram_msg("⚓ 아르 아빠님! 무전기가 정상 작동 중입니다!")
            st.toast("텔레그램 무전 완료!")
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
            st.error("비밀번호가 틀렸습니다.")
else:
    st.title("📈 실시간 김프 감시 대시보드")
    
    # 데이터 가져오기
    u_price, ex_rate, kimp_val = get_kimp_data()
    
    if u_price and ex_rate:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("업비트 USDT", f"{u_price:,.1f} 원")
        with col2:
            st.metric("현재 환율 (USD/KRW)", f"{ex_rate:,.1f} 원")
        with col3:
            # 김프 1% 기준 색상
            color = "normal" if kimp_val > 1.0 else "inverse"
            st.metric("실시간 김프", f"{kimp_val:.2f} %", delta=f"{kimp_val-1.0:.2f}%", delta_color=color)

        st.write("---")
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초마다 갱신)")
        
        # 10초 뒤 자동 새로고침
        time.sleep(10)
        st.rerun()
    else:
        st.warning("🔄 데이터 낚시 중... 잠시만 기다려주세요.")
        time.sleep(3)
        st.rerun()
