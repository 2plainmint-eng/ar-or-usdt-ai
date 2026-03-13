import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 🔐 1. 비밀 금고 정보
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

# 💰 2. 데이터 낚시 함수 (오류 수정 버전)
def get_exchange_data(url, key_path):
    try:
        res = requests.get(url, timeout=10).json()
        for key in key_path:
            res = res[key]
        return float(res)
    except:
        return None

# 🌟 3. 페이지 설정
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")

# 🛠️ 4. 시스템 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'kimp_history' not in st.session_state:
    st.session_state['kimp_history'] = []

# --- 메인 화면 로직 ---

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔐 AI 오두막 보안 시스템</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        input_pw = st.text_input("오두막 열쇠 (aror737)", type="password")
        if st.button("입장하기", use_container_width=True):
            if input_pw == "aror737":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("열쇠가 틀렸습니다!")
else:
    st.markdown("<h1 style='text-align: center; color: #26A17B;'>📈 실시간 김프 감시 대시보드</h1>", unsafe_allow_html=True)
    st.write("---")

    # [데이터 수집]
    up_price = get_exchange_data("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
    bn_price = get_exchange_data("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
    ok_price = get_exchange_data("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])
    ex_rate = get_exchange_data("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
    
    if up_price:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🇰🇷 Upbit", f"{up_price:,.1f}원")
        c2.metric("🔶 Binance", f"{bn_price:.4f}$" if bn_price else "대기 중")
        c3.metric("🖤 OKX", f"{ok_price:.4f}$" if ok_price else "대기 중")
        
        # 💡 수치 계산 로직 수정 (Binance나 OKX 중 있는 것만 평균내기)
        valid_prices = [p for p in [bn_price, ok_price] if p is not None]
        
        if valid_prices and ex_rate:
            avg_global = sum(valid_prices) / len(valid_prices)
            k_val = ((up_price / (avg_global * ex_rate)) - 1) * 100
            
            color = "normal" if k_val > 0 else "inverse"
            c4.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
            
            # 차트 기록 업데이트
            now_time = datetime.now().strftime('%H:%M:%S')
            st.session_state['kimp_history'].append({"시간": now_time, "김프": k_val})
            if len(st.session_state['kimp_history']) > 30:
                st.session_state['kimp_history'].pop(0)
        else:
            c4.metric("📊 실시간 김프", "계산 중...")

        # 📊 그래프 영역
        if st.session_state['kimp_history']:
            df = pd.DataFrame(st.session_state['kimp_history'])
            st.write("---")
            st.subheader("📉 김프 실시간 변화 차트")
            st.line_chart(df.set_index("시간"))

        st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 감시)")
        
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("로그아웃"):
                st.session_state['logged_in'] = False
                st.rerun()

        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 그물을 던졌습니다. 잠시만 기다려주세요...")
        time.sleep(3)
        st.rerun()
