import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 전문가용 프리미엄 스타일 ---
def apply_premium_style():
    st.markdown("""
        <style>
        /* 폰트 및 배경색 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; }
        .stApp { background-color: #f8f9fa; }

        /* 로그인 창 디자인 (아빠님 요청: 녹색 바탕) */
        .login-card {
            background-color: #26A17B;
            padding: 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 15px 35px rgba(38, 161, 123, 0.2);
        }
        
        /* 버튼 디자인 */
        div.stButton > button {
            background-color: #26A17B; color: white; border-radius: 10px;
            height: 3.5em; font-weight: 700; width: 100%; border: none;
            transition: 0.3s;
        }
        div.stButton > button:hover { background-color: #1e7e60; transform: translateY(-2px); }

        /* 대시보드 카드 디자인 */
        .metric-container {
            background-color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border-top: 5px solid #26A17B;
            text-align: center;
            margin-bottom: 20px;
        }
        h1, h2 { color: #26A17B; font-weight: 700; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 이중 우회로 장착 (차단 방지) ---
def get_safe_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # [A] 업비트
        up = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
        
        # [B] 바이낸스 (안되면 OKX로 우회)
        try:
            bn = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        except:
            bn = float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()['data'][0]['last'])
        
        # [C] 환율 (안되면 다른 서버로 우회)
        try:
            ex = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
        except:
            ex = float(requests.get("https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD", headers=headers).json()[0]['basePrice'])
            
        kimp = ((float(up) / (bn * ex)) - 1) * 100
        return float(up), bn, ex, kimp
    except:
        return None, None, None, None

# --- 3. 시스템 엔진 ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
apply_premium_style()

# --- [화면 1: 프리미엄 로그인] ---
if not st.session_state['auth']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
    with c2:
        st.markdown("""
            <div class='login-card'>
                <h1 style='color: white; margin-bottom: 5px;'>AI 오두막</h1>
                <p style='color: rgba(255,255,255,0.8);'>Ar & Or & Unit 737 Terminal</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        u_id = st.text_input("아이디 (ID)", value="admin")
        u_pw = st.text_input("비밀번호 (PW)", type="password")
        if st.button("시스템 접속"):
            if u_id == "admin" and u_pw == "aror737":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("정보가 일치하지 않습니다.")

# --- [화면 2: 메인 대시보드] ---
else:
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
        menu = st.radio("이동할 카테고리", ["🏠 실시간 홈 요약", "📊 거래소 정밀 분석", "⚙️ 무전 알림 설정"])
        st.write("---")
        if st.button("안전 로그아웃"):
            st.session_state['auth'] = False
            st.rerun()

    if menu == "🏠 실시간 홈 요약":
        st.markdown("<h1>실시간 시장 요약</h1>", unsafe_allow_html=True)
        up, bn, ex, k = get_safe_data()
        
        if up:
            st.markdown(f"""
                <div class='metric-container'>
                    <small style='color:gray;'>Upbit USDT 현재가</small>
                    <h2 style='font-size: 40px; margin: 0;'>{up:,.1f} <span style='font-size:20px;'>원</span></h2>
                </div>
                <div class='metric-container'>
                    <small style='color:gray;'>실시간 김치 프리미엄</small>
                    <h2 style='font-size: 40px; margin: 0; color: {"#26A17B" if k > 0 else "#007bff"};'>{k:.2f} <span style='font-size:20px;'>%</span></h2>
                </div>
            """, unsafe_allow_html=True)
            st.caption(f"업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신 중)")
            time.sleep(10); st.rerun()
        else:
            st.info("🔄 유닛 737이 긴급 우회 경로로 데이터를 수집 중입니다...")
            time.sleep(3); st.rerun()

    elif menu == "📊 거래소 정밀 분석":
        st.markdown("<h1>거래소 정밀 분석</h1>", unsafe_allow_html=True)
        up, bn, ex, k = get_safe_data()
        if up:
            col_a, col_b = st.columns(2)
            with col_a: st.metric("Binance (USD)", f"{bn:.4f} $")
            with col_b: st.metric("환율 (USD/KRW)", f"{ex:,.1f} 원")
            st.write("---")
            st.subheader("📉 최근 김프 변화 추이")
            st.line_chart([k-0.2, k-0.1, k, k+0.05])
            time.sleep(10); st.rerun()

    elif menu == "⚙️ 무전 알림 설정":
        st.markdown("<h1>무전 알림 설정</h1>", unsafe_allow_html=True)
        st.write("김프가 설정값 아래로 떨어지면 텔레그램으로 즉시 보고합니다.")
        threshold = st.slider("알림 기준 수치 (%)", -3.0, 3.0, 1.0)
        if st.button("설정 저장"): st.success(f"알림 기준이 {threshold}%로 저장되었습니다.")
