import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 아빠님의 강화된 클린 & 초고대비 스타일
def apply_ghost_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        
        /* 🧹 [배지 & 관리자 도구 완벽 박멸] */
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden !important; height: 0 !important; }
        .stAppDeployButton { display:none !important; }
        
        /* 메인 컨테이너 패딩 제거 (아빠님 조언) */
        .st-emotion-cache-1y4p8pa, .block-container { padding: 0 !important; margin: 0 !important; }
        
        /* 💡 [초고대비] 배경 검정, 글자 형광 화이트 */
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -60px; }
        
        /* 지표 숫자 (초강력 가독성) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: clamp(2.2rem, 10vw, 3.8rem) !important;
            font-weight: 900 !important;
            text-shadow: 2px 2px 8px rgba(0,0,0,1);
        }
        
        /* 지표 라벨 (민트 컬러) */
        [data-testid="stMetricLabel"] p {
            color: #26A17B !important;
            font-size: clamp(1rem, 5vw, 1.3rem) !important;
            font-weight: 700 !important;
        }

        /* 메뉴 라디오 스타일 */
        div[data-testid="stRadio"] > label { color: #ffffff !important; font-weight: 900 !important; }
        div[data-baseweb="radio"] { background-color: #1e2129; border-radius: 12px; padding: 12px; border: 2px solid #26A17B; }

        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.8rem, 8vw, 2.5rem); margin-bottom: 25px; }
        .trade-box { background-color: #1e2129; padding: 25px; border-radius: 20px; border: 1px solid #333; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진
def fetch_now(target):
    try:
        if target == "upbit": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        elif target == "binance": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        elif target == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except: return None

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'qty' not in st.session_state: st.session_state['qty'] = 0.0
if 'avg' not in st.session_state: st.session_state['avg'] = 0.0
if 'logs' not in st.session_state: st.session_state['logs'] = []

apply_ghost_clean_style()

# 🛡️ [아빠님 솔루션] 1단계: 플레이스홀더로 메인 화면 감싸기
main_placeholder = st.empty()

# 🛡️ [아빠님 솔루션] 2단계: 로그인 전환 잔상 강제 소탕
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:35px; border-radius:25px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private Solution</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="pw_input_v25")
        if st.button("시스템 접속", key="login_btn_v25"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty()  # 핵심: 이전 UI 즉시 파괴
                time.sleep(0.15)         # 프론트엔드 숨 고르기
                st.rerun()
            else: st.error("열쇠가 맞지 않습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 로그인 성공 시에만 여기까지 도달
# ---------------------------------------------------------

# 모드 선택 (위젯 Key 추가)
mode = st.radio("📡 오두막 제어 모드", ["📊 실시간 김프", "💹 가상 매매 터미널"], horizontal=True, key="mode_selector")

# 데이터 수집
up = fetch_now("upbit"); bn = fetch_now("binance"); ex = fetch_now("ex")
bn_k = (bn * ex) if (bn and ex) else 0
k_val = ((up / bn_k) - 1) * 100 if (up and bn_k) else 0.0

if mode == "📊 실시간 김프":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원")
    with c3: st.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).strftime('%H:%M:%S')
    st.session_state['logs'].append({"시간": now, "김프": k_val})
    if len(st.session_state['logs']) > 30: st.session_state['logs'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['logs']).set_index("시간"))
    st.caption(f"최근 업데이트: {now} (15초 자동 감시 중)")
    
    # 아빠님 제안대로 부하를 줄이기 위해 15초로 조정
    time.sleep(15); st.rerun()

elif mode == "💹 가상 매매 터미널":
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    
    # 수익 계산
    pnl = (st.session_state['qty'] * up) - (st.session_state['qty'] * st.session_state['avg']) if st.session_state['qty'] > 0 else 0
    pnl_p = (pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0) else 0
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown(f"<div class='trade-box'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p></div>", unsafe_allow_html=True)
    with col_w2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-box'><h3>📈 투자 손익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_p:.1f}%)</h2></div>", unsafe_allow_html=True)

    st.write("---")
    m1, m2 = st.columns(2)
    with m1:
        amt = st.number_input("매수 금액(원)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0, key="buy_input")
        if st.button("🚀 풀매수", key="buy_btn"):
            if up > 0 and amt > 0:
                new_q = amt / up
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (new_q * up)) / (st.session_state['qty'] + new_q)
                st.session_state['qty'] += new_q
                st.session_state['cash'] -= amt
                st.success("매수 완료!"); time.sleep(0.5); st.rerun()

    with m2:
        if st.button("💰 전량 매도", key="sell_btn"):
            if st.session_state['qty'] > 0:
                gain = st.session_state['qty'] * up
                st.session_state['cash'] += gain
                st.session_state['qty'] = 0; st.session_state['avg'] = 0
                st.success("전량 매도 완료!"); time.sleep(0.5); st.rerun()

with st.sidebar:
    st.info(f"⚓ 아르 아빠님 접속 중")
    if st.button("🚪 안전 로그아웃", key="logout_btn"):
        st.session_state['auth'] = False; st.rerun()
