import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 아빠님이 좋아하셨던 고대비 스타일 복구
def apply_final_revert_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 (쨍한 화이트) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important; font-size: clamp(1.8rem, 8vw, 3rem) !important;
            font-weight: 900 !important; text-shadow: 1px 1px 2px rgba(0,0,0,1);
        }
        
        /* 지표 라벨 (민트색) */
        [data-testid="stMetricLabel"] p {
            color: #26A17B !important; font-size: clamp(0.9rem, 4vw, 1.2rem) !important; font-weight: 700 !important;
        }

        .main-title { text-align: center; color: #26A17B; font-weight: 900; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 25px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 5px solid #26A17B !important; padding: 20px !important; border-radius: 15px !important; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 10px; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진 (하나라도 실패하면 다른 거래소 가격이라도 가져옴)
def get_safe_price(exchange):
    try:
        if exchange == "up": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        if exchange == "bn": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()['price'])
        if exchange == "ok": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        if exchange == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
    except: return None

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'qty' not in st.session_state: st.session_state['qty'] = 0.0
if 'avg' not in st.session_state: st.session_state['avg'] = 0.0
if 'history' not in st.session_state: st.session_state['history'] = []

apply_final_revert_style()

# 🛡️ [철벽 보안] 로그인 검문소 (잔상 방지)
main_placeholder = st.empty()
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_key")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty(); time.sleep(0.15); st.rerun()
            else: st.error("틀렸습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드
# ---------------------------------------------------------

# 1. 상단 메뉴 선택 (가장 안정적인 방식)
st.write("---")
col_m1, col_m2 = st.columns(2)
with col_m1: 
    show_kimp = st.button("📊 실시간 김프 보기", use_container_width=True)
    if show_kimp: st.session_state['menu'] = "kimp"
with col_m2: 
    show_trade = st.button("💹 가상 매매 하기", use_container_width=True)
    if show_trade: st.session_state['menu'] = "trade"

if 'menu' not in st.session_state: st.session_state['menu'] = "kimp"

# 데이터 수집
up_p = get_safe_price("up"); bn_p = get_safe_price("bn"); ok_p = get_safe_price("ok"); ex_r = get_safe_price("ex")
bn_k = (bn_p * ex_r) if (bn_p and ex_r) else None
ok_k = (ok_p * ex_r) if (ok_p and ex_r) else None
avg_global = [p for p in [bn_k, ok_k] if p]
k_val = ((up_p / (sum(avg_global)/len(avg_global))) - 1) * 100 if (up_p and avg_global) else 0.0

# [메인 화면 1: 김프]
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_p:,.0f}원" if up_p else "대기")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
    
    st.write("---")
    res1, res2 = st.columns(2)
    with res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    with res2: st.metric("💵 기준 환율", f"{ex_r:,.1f}원" if ex_r else "대기")
    
    # 차트
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).strftime('%H:%M:%S')
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    time.sleep(15); st.rerun()

# [메인 화면 2: 가상 매매]
else:
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    pnl = (st.session_state['qty'] * up_p) - (st.session_state['qty'] * st.session_state['avg']) if (st.session_state['qty'] > 0 and up_p) else 0
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"<div style='background-color:#1e2129; padding:20px; border-radius:15px; border:1px solid #333;'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p></div>", unsafe_allow_html=True)
    with col_v2:
        st.markdown(f"<div style='background-color:#1e2129; padding:20px; border-radius:15px; border:1px solid #333;'><h3>📈 투자 손익</h3><h2>{pnl:,.0f}원</h2><p>현재가: {up_p:,.0f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    if st.button("🚀 100만원 어치 매수"):
        if up_p and st.session_state['cash'] >= 1000000:
            new_q = 1000000 / up_p
            st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + 1000000) / (st.session_state['qty'] + new_q)
            st.session_state['qty'] += new_q
            st.session_state['cash'] -= 1000000
            st.rerun()
    if st.button("💰 전량 매도"):
        if up_p and st.session_state['qty'] > 0:
            st.session_state['cash'] += (st.session_state['qty'] * up_p)
            st.session_state['qty'] = 0; st.session_state['avg'] = 0
            st.rerun()

with st.sidebar:
    if st.button("🚪 로그아웃"):
        st.session_state['auth'] = False; st.rerun()
