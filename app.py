import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

# 1. 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI Pro", layout="wide")

# 2. 고대비 스타일 (안정성 강화)
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; border-radius: 12px !important; }
    div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: bold; height: 3rem; }
    .trade-card { background: #16191f; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 수집 (죽지 않는 좀비 로직)
@st.cache_data(ttl=5) # 5초 동안은 같은 데이터를 써서 서버 부담을 줄임
def get_data():
    res = {"up": 1400.0, "bn": 1.0, "ok": 1.0, "ex": 1380.0, "success": False}
    try:
        # 업비트
        up_r = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()
        res["up"] = float(up_r[0]['trade_price'])
        # 환율
        ex_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()
        res["ex"] = float(ex_r['rates']['KRW'])
        # 해외 (둘 중 하나만 성공해도 됨)
        try:
            bn_r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()
            res["bn"] = float(bn_r['price'])
            res["success"] = True
        except: pass
        return res
    except:
        return res

# 4. 세션 초기화
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp'}.items():
    if key not in st.session_state: st.session_state[key] = val

# 5. 메인 로직
if not st.session_state['auth']:
    st.title("🛡️ 보안 접속")
    pw = st.text_input("열쇠 (aror737)", type="password")
    if st.button("접속"):
        if pw == "aror737": 
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 상단 내비게이션
c_nav1, c_nav2 = st.columns(2)
if c_nav1.button("📊 김프 검증"): st.session_state['menu'] = "kimp"
if c_nav2.button("💹 가상 매매"): st.session_state['menu'] = "trade"

d = get_data()
kimp = ((d['up'] / (d['bn'] * d['ex'])) - 1) * 100 if d['success'] else 0.0

if st.session_state['menu'] == "kimp":
    st.header("⚓ USDT 실시간 검증")
    m1, m2, m3 = st.columns(3)
    m1.metric("🇰🇷 업비트", f"{d['up']:,.0f}원")
    m2.metric("📊 김프", f"{kimp:.2f}%")
    m3.metric("💵 환율", f"{d['ex']:,.1f}원")
    
    if st.button("🔄 수동 새로고침"):
        st.rerun()

else:
    st.header("💹 가상 매매 터미널")
    # 지갑 정보
    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f"<div class='trade-card'><h3>💳 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p></div>", unsafe_allow_html=True)
    
    # 매수/매도 로직 (v4.5와 동일하지만 안정적으로 배치)
    trade_q = st.number_input("수량", value=1000.0)
    if st.button("🚀 즉시 매수"):
        cost = trade_q * d['up']
        if st.session_state['cash'] >= cost:
            st.session_state['cash'] -= cost
            st.session_state['qty'] += trade_q
            st.success("매수 완료")
            st.rerun()
    
    if st.button("💸 즉시 매도"):
        if st.session_state['qty'] >= trade_q:
            st.session_state['cash'] += trade_q * d['up']
            st.session_state['qty'] -= trade_q
            st.warning("매도 완료")
            st.rerun()
