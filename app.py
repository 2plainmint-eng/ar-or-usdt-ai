import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 기본 설정
st.set_page_config(page_title="아르아빠 USDT Pro", layout="wide")

# 2. 🎨 [디자인] 깨지지 않는 블랙 & 그린 스타일
def apply_style():
    st.markdown("""
        <style>
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; border-radius: 12px !important; padding: 15px !important; }
        .pnl-card { background-color: #16191f; padding: 20px; border-radius: 15px; border: 1px solid #333; border-left: 5px solid #26A17B; margin-bottom: 20px; }
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; height: 3.5rem; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 (거래소별 투명하게 추출)
def fetch_trading_data():
    res = {"up": 0, "bn": 0, "ok": 0, "ex": 1380.0}
    try:
        # 업비트
        res["up"] = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        # 환율
        res["ex"] = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
        # 바이낸스 & OKX (개별 호출로 근거 확보)
        try: res["bn"] = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()['price'])
        except: pass
        try: res["ok"] = float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        except: pass
    except: pass
    return res

# 4. 세션 초기화 (로그인 및 지갑)
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_style()

# 🛡️ 로그인 시스템 (복구)
if not st.session_state['auth']:
    st.markdown("<br><br><h1 style='text-align:center; color:#26A17B;'>AI 오두막 보안 접속</h1>", unsafe_allow_html=True)
    pw = st.text_input("시스템 열쇠 (PW)", type="password")
    if st.button("시스템 가동") and pw == "aror737":
        st.session_state['auth'] = True
        st.rerun()
    st.stop()

# --- 메인 데이터 로드 ---
d = fetch_trading_data()
f_prices = [p for p in [d['bn'], d['ok']] if p > 0]
f_avg = sum(f_prices)/len(f_prices) if f_prices else 1.0
f_price_krw = f_avg * d['ex']
kimp = ((d['up'] / f_price_krw) - 1) * 100 if f_price_krw > 0 else 0.0

# --- 상단: 데이터 근거 (투명성) ---
st.title("⚓ USDT 실시간 검증 터미널")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🇰🇷 업비트", f"{d['up']:,}원")
c2.metric("🔶 바이낸스", f"{d['bn']*d['ex']:,.1f}원" if d['bn']>0 else "연결지연")
c3.metric("🖤 OKX", f"{d['ok']*d['ex']:,.1f}원" if d['ok']>0 else "연결지연")
c4.metric("📊 김프", f"{kimp:.2f}%")

st.write("---")

# --- 중간: 실전 정산 계산기 (핵심) ---
# 현재가로 매도 시 수수료(0.05%) 공제 후 예상 수령액
sell_fee_rate = 0.0005
current_total_value = st.session_state['qty'] * d['up']
estimated_net_proceeds = current_total_value * (1 - sell_fee_rate)

# 투자 원금 (평단가 기준)
investment_principal = st.session_state['qty'] * st.session_state['avg']

# 최종 순이익 (수수료 공제 후 수령액 - 투자 원금)
net_pnl = estimated_net_proceeds - investment_principal
pnl_pct = (net_pnl / investment_principal * 100) if investment_principal > 0 else 0.0

st.subheader("📊 실시간 정산 시뮬레이션")
v1, v2 = st.columns(2)
with v1:
    st.markdown(f"""<div class='pnl-card'>
        <p>💳 <b>내 지갑 현황</b></p>
        <p>보유 현금: {st.session_state['cash']:,.0f}원</p>
        <p>보유 수량: {st.session_state['qty']:,.2f} USDT</p>
        <p>매수 평단: {st.session_state['avg']:,.1f}원</p>
    </div>""", unsafe_allow_html=True)

with v2:
    p_color = "#ff4b4b" if net_pnl > 0 else "#1c83e1" if net_pnl < 0 else "#ffffff"
    st.markdown(f"""<div class='pnl-card'>
        <p>💰 <b>지금 팔면 내 손에 들어올 돈 (수수료 공제 후)</b></p>
        <h2 style='color:{p_color};'>{net_pnl:,.0f}원 ({pnl_pct:+.2f}%)</h2>
        <p>예상 수령액: {estimated_net_proceeds:,.0f}원</p>
    </div>""", unsafe_allow_html=True)

# --- 하단: 주문 섹션 ---
st.write("---")
st.subheader("🛒 주문 실행")
trade_q = st.number_input("거래 수량 (USDT)", value=1000.0, step=100.0)

b1, b2 = st.columns(2)
if b1.button("🚀 즉시 매수"):
    cost = trade_q * d['up'] * (1 + 0.0005) # 매수 수수료 포함
    if st.session_state['cash'] >= cost:
        # 평단가 가중 평균 계산
        total_cost = (st.session_state['qty'] * st.session_state['avg']) + (trade_q * d['up'])
        st.session_state['qty'] += trade_q
        st.session_state['avg'] = total_cost / st.session_state['qty']
        st.session_state['cash'] -= cost
        st.success(f"{trade_q} USDT 매수 완료")
        time.sleep(0.5); st.rerun()
    else: st.error("현금이 부족합니다.")

if b2.button("💸 즉시 매도"):
    if st.session_state['qty'] >= trade_q:
        st.session_state['cash'] += (trade_q * d['up'] * (1 - 0.0005)) # 매도 수수료 공제
        st.session_state['qty'] -= trade_q
        if st.session_state['qty'] < 0.1: st.session_state['avg'] = 0
        st.warning(f"{trade_q} USDT 매도 완료")
        time.sleep(0.5); st.rerun()
    else: st.error("보유 수량이 부족합니다.")

st.info(f"💡 현재 환율: {d['ex']:.2f}원 | 데이터 갱신 시간: {datetime.now().strftime('%H:%M:%S')}")
