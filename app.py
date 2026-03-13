import streamlit as st
import requests
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 💰 2. 데이터 낚시 함수 (로그인 후에만 작동하도록 설계)
def get_kimp_data():
    try:
        up_url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
        up_res = requests.get(up_url, timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        ex_url = "https://api.exchangerate-api.com/v4/latest/USD"
        ex_res = requests.get(ex_url, timeout=5).json()
        ex_rate = float(ex_res['rates']['KRW'])
        
        kimp = ((up_price / ex_rate) - 1) * 100
        return up_price, ex_rate, kimp
    except:
        return None, None, None

# 🌟 3. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 🛠️ 4. 로그인 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 메인 로직 ---

# [상황 1] 아직 로그인을 안 했을 때 -> 로그인 창만 보여줌
if not st.session_state['logged_in']:
    st.title("🛡️ 아르아빠 AI 보안 시스템")
    st.write("인증되지 않은 사용자는 데이터에 접근할 수 없습니다.")
    st.write("---")
    
    col1, _ = st.columns([1, 1.5])
    with col1:
        # 아빠님이 고치고 싶어 하시던 로고도 여기에 다시 장착!
        st.markdown(f"<img src='https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png' width='80'>", unsafe_allow_html=True)
        input_id = st.text_input("아이디", value="admin")
        input_pw = st.text_input("비밀번호", type="password")
        
        if st.button("🚀 AI 시스템 접속"):
            if input_id == "admin" and input_pw == "aror737":
                st.session_state['logged_in'] = True
                st.rerun() # 성공하면 즉시 화면 갱신!
            else:
                st.error("비밀번호가 틀렸습니다. 다시 확인해 주세요.")

# [상황 2] 로그인에 성공했을 때만! -> 대시보드 오픈
else:
    st.title("📈 실시간 김프 현황판")
    
    # 사이드바 설정
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

    # 실시간 데이터 가져오기
    with st.spinner("유닛 737이 최신 데이터를 분석 중..."):
        u_price, ex_rate, k_val = get_kimp_data()
    
    if u_price and ex_rate:
        c1, c2, c3 = st.columns(3)
        c1.metric("업비트 USDT", f"{u_price:,.1f} 원")
        c2.metric("글로벌 환율", f"{ex_rate:,.1f} 원")
        
        # 김프 수치 (역프일 때는 파란색으로 표시됨)
        k_color = "normal" if k_val > 0 else "inverse"
        st.write("---")
        st.metric("실시간 김프", f"{k_val:.2f} %", delta=f"{k_val:.2f}%", delta_color=k_color)
        
        # 💡 [역프 알림] 지금처럼 김프가 마이너스일 때 알려주기!
        if k_val < 0:
            st.info(f"📢 현재 **역프리미엄({k_val:.2f}%)** 구간입니다. 해외보다 한국이 더 저렴하네요!")

        st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
        
        time.sleep(10)
        st.rerun()
    else:
        st.warning("🔄 데이터를 다시 불러오고 있습니다...")
        time.sleep(3)
        st.rerun()
