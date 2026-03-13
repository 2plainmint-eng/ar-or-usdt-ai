import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정 (모바일 강제 최적화)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 모바일 시인성 300% 강화 및 배지 강제 퇴출
def apply_final_reconstruction_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        
        /* 🧹 [배지 박멸] 화면 상단/하단 모든 시스템 요소 강제 퇴출 */
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
        div[class^="viewerBadge"], .viewerBadge_container__1QSob { position: absolute; top: -1000px !important; left: -1000px !important; }
        
        /* 💡 [초고대비] 모바일 시인성 극대화 */
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -60px; }
        
        /* 지표 숫자 (초강력 화이트) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-family: 'Noto Sans KR', sans-serif !important;
            font-size: clamp(2rem, 10vw, 3.5rem) !important;
            font-weight: 900 !important;
            text-shadow: 2px 2px 5px rgba(0,0,0,1);
        }
        
        /* 지표 이름 (밝은 민트색으로 구분) */
        [data-testid="stMetricLabel"] p {
            color: #26A17B !important;
            -webkit-text-fill-color: #26A17B !important;
            font-size: clamp(1rem, 5vw, 1.3rem) !important;
            font-weight: 700 !important;
        }

        /* 메뉴 라디오 버튼 (모바일 최적화) */
        div[data-testid="stRadio"] > label { color: #ffffff !important; font-weight: 900 !important; font-size: 1.2rem !important; }
        div[data-baseweb="radio"] { background-color: #1e2129; border-radius: 10px; padding: 10px; border: 1px solid #26A17B; }

        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.8rem, 8vw, 2.5rem); margin-bottom: 20px; }
        .trade-box { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진
def fetch_now(target):
    try:
        if target == "upbit": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        elif target == "binance": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        elif target == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except: return None

# 세션 관리 (자산 정보 보존)
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'qty' not in st.session_state: st.session_state['qty'] = 0.0
if 'avg' not in st.session_state: st.session_state['avg'] = 0.0
if 'logs' not in st.session_state: st.session_state['logs'] = []

apply_final_reconstruction_style()

# 🛡️ 로그인 검문소
if not st.session_state['auth']:
    st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private</p></div>", unsafe_allow_html=True)
    pw = st.text_input("열쇠 (PW)", type="password")
    if st.button("시스템 접속"):
        if pw == "aror737":
            st.session_state['auth'] = True
            time.sleep(0.1); st.rerun()
        else: st.error("틀렸습니다.")
    st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드
# ---------------------------------------------------------

# 1단계: 모드 선택 (화면 맨 위에 배치하여 '가상매매'를 못 찾을 수 없게 함)
mode = st.radio("📡 모드 선택", ["📊 실시간 김프", "💹 가상 매매 터미널"], horizontal=True)

# 데이터 실시간 로드
up = fetch_now("upbit"); bn = fetch_now("binance"); ex = fetch_now("ex")
bn_k = (bn * ex) if (bn and ex) else 0
k_val = ((up / bn_k) - 1) * 100 if (up and bn_k) else 0.0

if mode == "📊 실시간 김프":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원")
    with c3: st.metric("📊 김프", f"{k_val:.2f}%")
    
    st.write("---")
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).strftime('%H:%M:%S')
    st.session_state['logs'].append({"시간": now, "김프": k_val})
    if len(st.session_state['logs']) > 30: st.session_state['logs'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['logs']).set_index("시간"))
    st.caption(f"최근 갱신: {now} (12초 자동)")
    time.sleep(12); st.rerun()

elif mode == "💹 가상 매매 터미널":
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    
    # 수익률 계산
    cur_val = st.session_state['qty'] * up
    pnl = cur_val - (st.session_state['qty'] * st.session_state['avg']) if st.session_state['qty'] > 0 else 0
    pnl_p = (pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0) else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='trade-box'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p></div>", unsafe_allow_html=True)
    with col2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-box'><h3>📈 투자 손익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_p:.1f}%)</h2></div>", unsafe_allow_html=True)

    st.write("---")
    m1, m2 = st.columns(2)
    with m1:
        amt = st.number_input("매수 금액(원)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0)
        if st.button("🚀 풀매수"):
            if up > 0 and amt > 0:
                new_q = amt / up
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (new_q * up)) / (st.session_state['qty'] + new_q)
                st.session_state['qty'] += new_q
                st.session_state['cash'] -= amt
                st.success("매수 완료!"); time.sleep(1); st.rerun()

    with m2:
        if st.button("💰 전량 매도"):
            if st.session_state['qty'] > 0:
                gain = st.session_state['qty'] * up
                st.session_state['cash'] += gain
                st.session_state['qty'] = 0; st.session_state['avg'] = 0
                st.success("전량 매도 완료!"); time.sleep(1); st.rerun()

with st.sidebar:
    if st.button("🚪 로그아웃"):
        st.session_state['auth'] = False; st.rerun()
