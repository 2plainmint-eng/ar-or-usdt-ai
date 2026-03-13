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
        
        /* 기본 배경 및 폰트 */
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        h1, h2, h3, p { font-family: 'Noto Sans KR', sans-serif; }
        
        /* 메인 타이틀 */
        .main-title { 
            text-align: center; color: #26A17B; 
            font-family: 'Black Han Sans', sans-serif; 
            font-size: 2.5rem; margin-bottom: 25px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }

        /* 메트릭 카드 디자인 */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important;
            border: 1px solid #333 !important;
            border-top: 4px solid #26A17B !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }
        [data-testid="stMetricValue"] > div { font-size: 1.8rem !important; font-weight: 900 !important; color: #ffffff !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-size: 1rem !important; font-weight: 700 !important; }

        /* 거래 카드 */
        .trade-card {
            background-color: #16191f; border-radius: 15px;
            padding: 20px; border: 1px solid #26A17B; margin-bottom: 15px;
        }

        /* 버튼 커스텀 */
        div.stButton > button {
            background-color: #26A17B !important; color: white !important;
            border-radius: 10px; border: none; font-weight: 700; height: 3.5rem; width: 100%;
        }
        .full-btn div.stButton > button { background-color: #ff4b4b !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 (안전 장치 강화)
def fetch_all_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = {"up": 0.0, "bn": 0.0, "ok": 0.0, "ex": 1350.0} # 기본값
    
    try:
        # 업비트 (국내)
        res["up"] = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        # 환율
        res["ex"] = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
        # 바이낸스
        bn_data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()
        res["bn"] = float(bn_data['price'])
        # OKX
        ok_data = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()
        res["ok"] = float(ok_data['data'][0]['last'])
    except:
        pass # 에러 발생 시 초기값(0.0) 유지하여 화면 뻗음 방지
    return res

# 세션 상태 초기화
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp', 'history': []})

apply_pro_style()

# 🛡️ 로그인 (보안)
if not st.session_state['auth']:
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; text-align:center;'><h1>AI 터미널 접속</h1></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password")
        if st.button("시스템 가동") and pw == "aror737":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- 데이터 계산 ---
d = fetch_all_data()
global_avg_krw = ((d['bn'] + d['ok']) / 2 * d['ex']) if (d['bn'] > 0 and d['ok'] > 0) else (d['up'] if d['up'] > 0 else 1)
kimp = ((d['up'] / global_avg_krw) - 1) * 100 if global_avg_krw > 0 else 0.0
now = datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

# 상단 메뉴
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 실시간 김프 검증"): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 프로 가상 매매"): st.session_state['menu'] = "trade"

# --- 화면 1: 김프 검증 ---
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🇰🇷 업비트", f"{d['up']:,.0f}원")
    c2.metric("🔶 바이낸스", f"{d['bn']*d['ex']:,.1f}원" if d['bn']>0 else "연결중...")
    c3.metric("🖤 OKX", f"{d['ok']*d['ex']:,.1f}원" if d['ok']>0 else "연결중...")
    c4.metric("📊 김프", f"{kimp:.2f}%", delta=f"{kimp:.2f}%")

    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": kimp})
    if len(st.session_state['history']) > 20: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    time.sleep(8)
    st.rerun()

# --- 화면 2: 가상 매매 ---
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 정산 계산
    cur_val = st.session_state['qty'] * d['up']
    fee = cur_val * 0.0005
    est_net = cur_val - fee
    invested = st.session_state['qty'] * st.session_state['avg']
    pnl = est_net - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    v1, v2 = st.columns(2)
    v1.markdown(f"<div class='trade-card'><h3>💳 지갑 현황</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:,.2f} USDT</p><p>평단: {st.session_state['avg']:,.1f}원</p></div>", unsafe_allow_html=True)
    
    p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
    v2.markdown(f"<div class='trade-card'><h3>📊 예상 정산 수익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_pct:+.2f}%)</h2><p>현재가: {d['up']:,.1f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    trade_q = st.number_input("거래 수량 입력", value=1000.0, step=100.0)
    
    col_b, col_s = st.columns(2)
    if col_b.button("🚀 즉시 매수"):
        cost = trade_q * d['up'] * 1.0005
        if st.session_state['cash'] >= cost:
            st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_q * d['up'])) / (st.session_state['qty'] + trade_q)
            st.session_state['qty'] += trade_q
            st.session_state['cash'] -= cost
            st.rerun()
        else: st.error("잔액 부족")

    if col_s.button("💸 즉시 매도"):
        if st.session_state['qty'] >= trade_q:
            st.session_state['cash'] += (trade_q * d['up'] * 0.9995)
            st.session_state['qty'] -= trade_q
            if st.session_state['qty'] < 0.1: st.session_state['avg'] = 0
            st.rerun()
        else: st.error("수량 부족")

    if st.button("💎 전량 정산 (EXIT)", type="primary", use_container_width=True):
        st.session_state['cash'] += (st.session_state['qty'] * d['up'] * 0.9995)
        st.session_state['qty'] = 0; st.session_state['avg'] = 0
        st.balloons(); time.sleep(1); st.rerun()
