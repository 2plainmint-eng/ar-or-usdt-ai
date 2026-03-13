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

# 💰 3. 개별 데이터 낚시 함수 (한 명이라도 낚이면 성공!)
def get_exchange_data(url, key_path):
    try:
        res = requests.get(url, timeout=10).json()
        for key in key_path:
            res = res[key]
        return float(res)
    except:
        return None

# 🌟 4. 페이지 설정
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")

# 🛠️ 5. 시스템 초기화
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
    # 📈 대시보드 화면 (중앙 정렬)
    st.markdown("<h1 style='text-align: center; color: #26A17B;'>📈 실시간 김프 감시 대시보드</h1>", unsafe_allow_html=True)
    st.write("---")

    # [데이터 수집 시작]
    up_price = get_exchange_data("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
    bn_price = get_exchange_data("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
    ok_price = get_exchange_data("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])
    ex_rate = get_exchange_data("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
    
    # 하나라도 데이터가 들어왔다면 화면을 그립니다!
    if up_price or bn_price or ok_price:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🇰🇷 Upbit", f"{up_price:,.1f}원" if up_price else "대기 중")
        c2.metric("🔶 Binance", f"{bn_price:.4f}$" if bn_price else "대기 중")
        c3.metric("🖤 OKX", f"{ok_price:.4f}$" if ok_price else "대기 중")
        
        # 김프 계산 (데이터가 충분할 때만)
        if up_price and ex_rate:
            avg_global = (bn_price if bn_price else 1.0 + ok_price if ok_price else 1.0) / (2 if bn_price and ok_price else 1)
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
        
        # 사이드바 (로그아웃 버튼)
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("로그아웃"):
                st.session_state['logged_in'] = False
                st.rerun()

        time.sleep(10)
        st.rerun()
    else:
        st.info("🎣 유닛 737이 첫 번째 물고기를 낚는 중입니다... (약 5~10초 소요)")
        time.sleep(3)
        st.rerun()
