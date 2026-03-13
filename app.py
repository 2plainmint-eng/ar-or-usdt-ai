import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI Pro", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 실전 정산 UI 스타일
def apply_v39_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        
        /* 메트릭 카드 */
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: 1.8rem !important; font-weight: 900 !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }
        [data-testid="stMetric"] { 
            background-color: #1e2129 !important; 
            border-top: 4px solid #26A17B !important; 
            padding: 15px !important; 
            border-radius: 12px !important; 
        }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: 2.2rem; margin-bottom: 20px; }
        
        /* 버튼 스타일 */
        div.stButton > button { 
            background-color: #26A17B !important; color: white !important; 
            font-weight: 700; border-radius: 8px; border: none; height: 3em; width: 100%; 
        }
        .full-btn div.stButton > button { background-color: #ff4b4b !important; }
        
        .trade-card { 
            background-color: #1e2129; padding: 20px; border-radius: 15px; 
            border: 1px solid #333; margin-bottom: 10px; 
        }
        .profit-warning { 
            color: #ff4b4b; font-weight: 900; font-size: 1rem; 
            border: 2px solid #ff4b4b; padding: 10px; border-radius: 10px; 
            text-align: center; margin-bottom: 15px; background-color: rgba(255, 75, 75, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진 (캐싱 및 예외처리 강화)
@st.cache_data(ttl=600) # 환율은 10분마다 갱신
def get_exchange_rate():
    try:
        return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
    except:
        return 1350.0 # 예외 시 기본값

def fetch_prices():
    h = {'User-Agent': 'Mozilla/5.0'}
    data = {"up": None, "bn": None, "ok": None}
    try:
        data["up"] = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        # 바이낸스/OKX는 가격차이가 미세하므로 가중치 조절 가능
        data["bn"] = float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", headers=h, timeout=2).json()['price'])
        data["ok"] = float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
    except:
        pass
    return data

# 세션 초기화
if 'auth' not in st.session_state:
    st.session_state.update({
        'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 
        'menu': 'kimp', 'q_val': 100.0, 'history': []
    })

apply_v39_style()

# 🛡️ 로그인
if not st.session_state['auth']:
    st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Pro Terminal</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password")
        if st.button("시스템 접속") and pw == "aror737":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 📈 데이터 로드 및 계산
prices = fetch_prices()
ex = get_exchange_rate()
up = prices['up'] or 0.0

# 해외 평균가 (환율 적용)
global_prices = [p * ex for p in [prices['bn'], prices['ok']] if p]
global_avg = sum(global_prices) / len(global_prices) if global_prices else up
k_val = ((up / global_avg) - 1) * 100 if global_avg > 0 else 0.0
now = datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

# 상단 네비게이션
m1, m2 = st.columns(2)
if m1.button("📊 김프 검증"): st.session_state['menu'] = "kimp"
if m2.button("💹 가상 매매"): st.session_state['menu'] = "trade"

# --- 화면 1: 김프 검증 ---
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🇰🇷 업비트", f"{up:,.0f}원")
    c2.metric("🔶 바이낸스", f"{prices['bn']*ex:,.1f}원" if prices['bn'] else "대기")
    c3.metric("🖤 OKX", f"{prices['ok']*ex:,.1f}원" if prices['ok'] else "대기")
    c4.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    time.sleep(10)
    st.rerun()

# --- 화면 2: 가상 매매 ---
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 정산 계산식
    curr_total = st.session_state['qty'] * up
    fee = curr_total * 0.0005 # 업비트 수수료 0.05%
    est_net = curr_total - fee
    invested = st.session_state['qty'] * st.session_state['avg']
    pnl = est_net - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f"""<div class='trade-card'><h3>💳 지갑 현황</h3>
            <p>보유 현금: <b>{st.session_state['cash']:,.0f}원</b></p>
            <p>보유 수량: <b>{st.session_state['qty']:,.2f} USDT</b></p>
            <p>평균 단가: <b>{st.session_state['avg']:,.1f}원</b></p></div>""", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"""<div class='trade-card'><h3>📊 예상 정산 (수수료 제함)</h3>
            <h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_pct:+.2f}%)</h2>
            <p>현재가: {up:,.1f}원 / 김프: {k_val:.2f}%</p></div>""", unsafe_allow_html=True)
        if invested > 0 and pnl < 0 and (curr_total - invested) > 0:
            st.markdown("<div class='profit-warning'>⚠️ 경고: 세금/수수료 계산 시 실질 손실 구간입니다.</div>", unsafe_allow_html=True)

    # 매수/매도 컨트롤
    st.write("---")
    bq1, bq2, bq3, bq4 = st.columns(4)
    if bq1.button("100"): st.session_state['q_val'] = 100.0
    if bq2.button("500"): st.session_state['q_val'] = 500.0
    if bq3.button("1000"): st.session_state['q_val'] = 1000.0
    if bq4.button("3000"): st.session_state['q_val'] = 3000.0
    
    trade_q = st.number_input("거래 희망 수량", value=st.session_state['q_val'], step=50.0)
    
    col_buy, col_sell = st.columns(2)
    with col_buy:
        if st.button("🚀 즉시 매수"):
            cost = trade_q * up * 1.0005
            if st.session_state['cash'] >= cost:
                new_qty = st.session_state['qty'] + trade_q
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_q * up)) / new_qty
                st.session_state['qty'] = new_qty
                st.session_state['cash'] -= cost
                st.success(f"{trade_q} USDT 체결 완료")
                time.sleep(0.5); st.rerun()
            else: st.error("잔액이 부족합니다.")
            
    with col_sell:
        if st.button("💸 즉시 매도"):
            if st.session_state['qty'] >= trade_q:
                st.session_state['cash'] += (trade_q * up * 0.9995)
                st.session_state['qty'] -= trade_q
                if st.session_state['qty'] < 0.01: st.session_state['avg'] = 0
                st.warning(f"{trade_q} USDT 매도 완료")
                time.sleep(0.5); st.rerun()
            else: st.error("보유 수량이 부족합니다.")

    if st.button("💎 전량 정산 (EXIT)", use_container_width=True, type="primary"):
        if st.session_state['qty'] > 0:
            st.session_state['cash'] += (st.session_state['qty'] * up * 0.9995)
            st.session_state['qty'], st.session_state['avg'] = 0, 0
            st.balloons(); st.rerun()
