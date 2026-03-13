import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI Pro", layout="wide")

# 2. 🎨 [디자인] 절대 깨지지 않는 고대비 스타일
def apply_pro_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: 2.5rem; margin-bottom: 25px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; border-radius: 12px !important; padding: 15px !important; }
        [data-testid="stMetricValue"] > div { font-size: 1.8rem !important; font-weight: 900 !important; color: #ffffff !important; }
        .trade-card { background-color: #16191f; border-radius: 15px; padding: 20px; border: 1px solid #333; margin-bottom: 15px; border-left: 5px solid #26A17B; }
        div.stButton > button { background-color: #26A17B !important; color: white !important; border-radius: 10px; font-weight: 700; height: 3.5rem; width: 100%; border: none; }
        .full-btn div.stButton > button { background-color: #ff4b4b !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 (강화된 버전)
def fetch_all_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = {"up": 0.0, "bn": 0.0, "ok": 0.0, "ex": 1380.0}
    
    # 업비트
    try:
        res["up"] = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
    except: pass

    # 환율 (실패 시 1380원 고정)
    try:
        res["ex"] = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except: pass

    # 바이낸스 & OKX (동시 시도)
    try:
        r_bn = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()
        res["bn"] = float(r_bn['price'])
    except: pass
    
    try:
        r_ok = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()
        res["ok"] = float(r_ok['data'][0]['last'])
    except: pass

    return res

# 4. 세션 초기화
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp', 'history': [], 'q_val': 1000.0})

apply_pro_style()

# 🛡️ 로그인
if not st.session_state['auth']:
    st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; text-align:center; color:white;'><h1>AI 터미널 보안 접속</h1></div>", unsafe_allow_html=True)
    pw = st.text_input("열쇠 (PW)", type="password")
    if st.button("시스템 가동") and pw == "aror737":
        st.session_state['auth'] = True
        st.rerun()
    st.stop()

# --- 공통 데이터 처리 ---
d = fetch_all_data()
valid_foreign = [p for p in [d['bn'], d['ok']] if p > 0]
global_avg_krw = (sum(valid_foreign) / len(valid_foreign) * d['ex']) if valid_foreign else d['up']
kimp = ((d['up'] / global_avg_krw) - 1) * 100 if global_avg_krw > 0 else 0.0
now = datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

# 네비게이션
m1, m2 = st.columns(2)
if m1.button("📊 실시간 김프 검증"): st.session_state['menu'] = "kimp"
if m2.button("💹 프로 가상 매매"): st.session_state['menu'] = "trade"

# --- 화면 1: 김프 검증 ---
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🇰🇷 업비트", f"{d['up']:,.0f}원")
    c2.metric("🔶 바이낸스", f"{d['bn']*d['ex']:,.1f}원" if d['bn']>0 else "통신지연")
    c3.metric("🖤 OKX", f"{d['ok']*d['ex']:,.1f}원" if d['ok']>0 else "통신지연")
    c4.metric("📊 김프", f"{kimp:.2f}%", delta=f"{kimp:.2f}%")

    st.write("---")
    if global_avg_krw > 0:
        st.session_state['history'].append({"시간": now, "김프": kimp})
        if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    time.sleep(10)
    st.rerun()

# --- 화면 2: 가상 매매 터미널 ---
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 수익 계산 로직
    cur_val = st.session_state['qty'] * d['up']
    fee = cur_val * 0.0005
    est_net = cur_val - fee
    invested = st.session_state['qty'] * st.session_state['avg']
    pnl = est_net - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f"""<div class='trade-card'><h3>💳 내 지갑</h3>
            <p>보유 현금: <b>{st.session_state['cash']:,.0f}원</b></p>
            <p>보유 수량: <b>{st.session_state['qty']:,.2f} USDT</b></p>
            <p>평균 단가: <b>{st.session_state['avg']:,.1f}원</b></p></div>""", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"""<div class='trade-card'><h3>📊 예상 정산 수익</h3>
            <h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_pct:+.2f}%)</h2>
            <p>현재가: {d['up']:,.1f}원 / 예상 수수료: {fee:,.0f}원</p></div>""", unsafe_allow_html=True)

    st.write("---")
    
    # 수량 조절 퀵 버튼
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("100"): st.session_state['q_val'] = 100.0
    if q2.button("1000"): st.session_state['q_val'] = 1000.0
    if q3.button("5000"): st.session_state['q_val'] = 5000.0
    if q4.button("10000"): st.session_state['q_val'] = 10000.0
    
    trade_q = st.number_input("거래 수량 입력", value=float(st.session_state['q_val']), step=100.0)
    
    # 매수 매도 버튼
    cb, cs = st.columns(2)
    with cb:
        if st.button("🚀 즉시 매수"):
            cost = trade_q * d['up'] * 1.0005
            if st.session_state['cash'] >= cost:
                new_total_qty = st.session_state['qty'] + trade_q
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_q * d['up'])) / new_total_qty
                st.session_state['qty'] = new_total_qty
                st.session_state['cash'] -= cost
                st.success(f"{trade_q:,.0f} USDT 매수 완료")
                time.sleep(0.5); st.rerun()
            else: st.error("현금이 부족합니다.")

    with cs:
        if st.button("💸 즉시 매도"):
            if st.session_state['qty'] >= trade_q:
                st.session_state['cash'] += (trade_q * d['up'] * 0.9995)
                st.session_state['qty'] -= trade_q
                if st.session_state['qty'] < 0.1: st.session_state['avg'] = 0
                st.warning(f"{trade_q:,.0f} USDT 매도 완료")
                time.sleep(0.5); st.rerun()
            else: st.error("보유 수량이 부족합니다.")

    if st.button("💎 전량 정산 (ALL EXIT)", use_container_width=True, type="primary"):
        if st.session_state['qty'] > 0:
            st.session_state['cash'] += (st.session_state['qty'] * d['up'] * 0.9995)
            st.session_state['qty'], st.session_state['avg'] = 0, 0
            st.balloons(); time.sleep(1); st.rerun()
