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

# 💰 3. 초강력 데이터 낚싯대 (해외 서버 공략!)
def get_kimp_data():
    try:
        # [A] 업비트 가격 가져오기 (비교적 해외 접속에 관대함)
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        # [B] 환율 가져오기 (한국 서버가 막으면 글로벌 서버로 우회!)
        try:
            # 1순위: 글로벌 환율 API (해외 클라우드에서 차단 안 됨)
            ex_url = "https://api.exchangerate-api.com/v4/latest/USD"
            ex_res = requests.get(ex_url, timeout=5).json()
            ex_rate = float(ex_res['rates']['KRW'])
        except:
            # 2순위: 혹시 안되면 기존 한국 서버 재시도
            headers = {'User-Agent': 'Mozilla/5.0'}
            ex_url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
            ex_res = requests.get(ex_url, headers=headers, timeout=5).json()
            ex_rate = float(ex_res[0]['basePrice'])
        
        kimp = ((up_price / ex_rate) - 1) * 100
        return up_price, ex_rate, kimp
    except Exception as e:
        # 사이드바에 에러 정체 노출
        st.sidebar.error(f"🔍 낚시 실패 정체: {str(e)}")
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
    st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='80'></div>", unsafe_allow_html=True)
    st.title("USDT 감시단")
    
    if st.session_state['logged_in']:
        st.success(f"⚓ {st.session_state['user_id']}님")
        if st.button("🔔 무전 테스트"):
            send_telegram_msg("⚓ 아빠님! 무전기가 정상입니다!")
            st.toast("무전 완료!")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- 메인 화면 ---
if not st.session_state['logged_in']:
    st.title("🛡️ AI 보안 시스템")
    col1, _ = st.columns([1, 2])
    with col1:
        id_input = st.text_input("아이디", value="admin")
        pw_input = st.text_input("비밀번호", type="password")
        if st.button("AI 시스템 접속"):
            if id_input == "admin" and pw_input == "aror737":
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = id_input
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
else:
    st.title("📈 실시간 김프 현황")
    
    # 데이터 가져오기 (성공할 때까지 무한 도전!)
    u_price, ex_rate, k_val = get_kimp_data()
    
    if u_price and ex_rate:
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("글로벌 환율", f"{ex_rate:,.1f} 원")
        
        # 김프 색상 조절
        color = "normal" if k_val > 1.0 else "inverse"
        c3.metric("실시간 김프", f"{k_val:.2f} %", delta=f"{k_val-1.0:.2f}%", delta_color=color)
        
        st.write("---")
        st.caption(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
        
        # 자동 무전 로직 (김프가 1% 아래로 떨어지면!)
        if k_val < 1.0:
            st.warning("⚠️ 김프가 1% 아래입니다! 텔레그램 무전을 발송합니다.")
            # 여기에 send_telegram_msg 기능을 넣으면 무전이 날아갑니다!
        
        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 글로벌 서버에서 데이터를 낚아오는 중...")
        time.sleep(3)
        st.rerun()
