import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 💰 2. 글로벌 데이터 낚시 함수 (업비트 + 바이낸스 + OKX)
def get_global_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # [A] 업비트 USDT 가격
        up_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()
        up_price = float(up_res[0]['trade_price'])
        
        # [B] 바이낸스 USDT/USD 가격 (보통 1달러 근처)
        bin_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()
        bin_price = float(bin_res['price'])
        
        # [C] OKX USDT/USD 가격
        okx_res = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()
        okx_price = float(okx_res['data'][0]['last'])
        
        # [D] 글로벌 환율
        ex_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        ex_rate = float(ex_res['rates']['KRW'])
        
        # 김프 계산 (업비트 가격 / (바이낸스 가격 * 환율))
        global_avg = (bin_price + okx_price) / 2
        kimp = ((up_price / (global_avg * ex_rate)) - 1) * 100
        
        return up_price, bin_price, okx_price, ex_rate, kimp
    except:
        return None, None, None, None, None

# 🌟 3. 페이지 설정
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")

# 🛠️ 4. 시스템 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'kimp_history' not in st.session_state:
    st.session_state['kimp_history'] = []

# --- 메인 화면 로직 ---

if not st.session_state['logged_in']:
    # 🏠 로그인 화면 (중앙 정렬)
    st.markdown("<h2 style='text-align: center;'>🔐 AI 오두막 보안 시스템</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        input_pw = st.text_input("오두막 열쇠", type="password")
        if st.button("입장하기", use_container_width=True):
            if input_pw == "aror737":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("열쇠가 틀렸습니다!")
else:
    # 📈 대시보드 화면 (중앙 정렬 제목)
    st.markdown("<h1 style='text-align: center; color: #26A17B;'>📈 실시간 김프 감시 대시보드</h1>", unsafe_allow_html=True)
    st.write("---")

    # 데이터 가져오기
    up, bn, ok, ex, k = get_global_data()
    
    if up:
        # 1. 상단 지표 (4열 구성)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🇰🇷 Upbit (USDT)", f"{up:,.1f}원")
        c2.metric("🔶 Binance (USD)", f"{bn:.4f}$")
        c3.metric("🖤 OKX (USD)", f"{ok:.4f}$")
        color = "normal" if k > 0 else "inverse"
        c4.metric("📊 실시간 김프", f"{k:.2f}%", delta=f"{k:.2f}%", delta_color=color)

        # 2. 📊 김프 흐름 그래프
        now_time = datetime.now().strftime('%H:%M:%S')
        st.session_state['kimp_history'].append({"시간": now_time, "김프": k})
        if len(st.session_state['kimp_history']) > 30: # 30개까지 기록
            st.session_state['kimp_history'].pop(0)
        
        df = pd.DataFrame(st.session_state['kimp_history'])
        st.write("---")
        st.subheader("📉 김프 실시간 변화 (Binance/OKX 평균 기준)")
        st.line_chart(df.set_index("시간"))

        st.caption(f"최근 갱신: {now_time} (10초 자동 감시 중)")
        
        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 글로벌 거래소를 돌며 데이터를 모으고 있습니다...")
        time.sleep(3)
        st.rerun()
