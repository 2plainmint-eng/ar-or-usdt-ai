import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI Pro", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 그리드 레이아웃 스타일
def apply_final_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: 2.5rem; margin-bottom: 25px; }
        
        /* 메트릭 카드 */
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; border-radius: 12px !important; padding: 15px !important; }
        [data-testid="stMetricValue"] > div { font-size: 1.8rem !important; font-weight: 900 !important; color: #ffffff !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }

        /* 거래 카드 */
        .trade-card { background-color: #16191f; border-radius: 15px; padding: 25px; border: 1px solid #333; margin-bottom: 20px; border-left: 5px solid #26A17B; }
        
        /* 버튼 스타일 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 10px; border: none; height: 3.5rem; width: 100%; }
        .full-btn div.stButton > button { background-color: #ff4b4b !important; }
        
        /* 수량 입력칸 */
        .stNumberInput input { background-color: #1e2129 !important; color: white !important; border: 1px solid #333 !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진 (안전 + 정확)
@st.cache_data(ttl=10)
def fetch_master_data():
    res = {"up": 0.0, "bn": 0.0, "ex": 1380.0, "success": False}
    try:
        # 업비트 가격
        up_req = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()
        res["up"] = float(up_req[0]['trade_price'])
        # 환율
        ex_req = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()
        res["ex"] = float(ex_req['rates']['KRW'])
        # 바이낸스 (해외 가격)
        bn_req = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()
        res["bn"] = float(bn_req['price'])
        res["success"] = True
    except:
        pass
    return res

# 4. 세션 초기화
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp', 'q_val': 1000.0}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_final_style()

# 🛡️ 로그인
if not st.session_state['auth']:
    st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>AI 터미널 보안 접속</div>", unsafe_allow_html=True)
    pw = st.text_input("열쇠 (PW)", type="password")
    if st.button("시스템 접속") and pw == "aror737":
        st.session_state['auth'] = True
        st.rerun()
    st.stop()

# --- 데이터 준비 ---
d = fetch_master_data()
# 김프 계산 (해외 가격이 0이면 업비트 가격과 환율로 역산)
foreign_price_krw = (d['bn'] * d['ex']) if d['bn'] > 0 else d['ex']
kimp = ((d['up'] / foreign_price_krw) - 1) * 100 if foreign_price_krw > 0 else 0.0

# 상단 내비
n1, n2 = st.columns(2)
if n1.button("📊 실시간 김프 검증"): st.session_state['menu'] = "kimp"
if n2.button("💹 프로 가상 매매"): st.session_state['menu'] = "trade"

# --- 화면 1: 김프 검증 ---
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🇰🇷 업비트", f"{d['up']:,.0f}원")
    c2.metric("🔶 바이낸스", f"{foreign_price_krw:,.1f}원" if d['bn'] > 0 else "연결대기")
    c3.metric("📊 김프", f"{kimp:.2f}%", delta=f"{kimp:.2f}%")
    c4.metric("💵 환율", f"{d['ex']:,.1f}원")
    
    st.write("---")
    if st.button("🔄 즉시 새로고침"): st.rerun()
    time.sleep(15); st.rerun()

# --- 화면 2: 가상 매매 ---
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 수익률 계산
    cur_val = st.session_state['qty'] * d['up']
    fee = cur_val * 0.0005
    est_net = cur_val - fee
    invested = st.session_state['qty'] * st.session_state['avg']
    pnl = est_net - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f"<div class='trade-card'><h3>💳 지갑 현황</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.1f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📊 예상 정산 수익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_pct:+.2f}%)</h2><p>현재가: {d['up']:,.1f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    # 수량 조절 버튼 그리드
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("100"): st.session_state['q_val'] = 100.0
    if q2.button("1000"): st.session_state['q_val'] = 1000.0
    if q3.button("5000"): st.session_state['q_val'] = 5000.0
    if q4.button("전량"): st.session_state['q_val'] = st.session_state['qty'] if st.session_state['qty'] > 0 else 1000.0

    trade_q = st.number_input("거래 수량", value=float(st.session_state['q_val']), step=100.0)
    
    b_buy, b_sell = st.columns(2)
    with b_buy:
        if st.button("🚀 즉시 매수"):
            cost = trade_q * d['up'] * 1.0005
            if st.session_state['cash'] >= cost:
                new_qty = st.session_state['qty'] + trade_q
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_q * d['up'])) / new_qty
                st.session_state['qty'] = new_qty
                st.session_state['cash'] -= cost
                st.rerun()
            else: st.error("잔액 부족")
    
    with b_sell:
        if st.button("💸 즉시 매도"):
            if st.session_state['qty'] >= trade_q:
                st.session_state['cash'] += (trade_q * d['up'] * 0.9995)
                st.session_state['qty'] -= trade_q
                if st.session_state['qty'] < 0.1: st.session_state['avg'] = 0
                st.rerun()
            else: st.error("수량 부족")

    if st.button("💎 전량 정산 (ALL EXIT)", type="primary"):
        st.session_state['cash'] += (st.session_state['qty'] * d['up'] * 0.9995)
        st.session_state['qty'], st.session_state['avg'] = 0, 0
        st.balloons(); time.sleep(1); st.rerun()
