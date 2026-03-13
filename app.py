import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 모든 버튼 스타일 통합
def apply_v36_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 및 라벨 */
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.2rem, 5vw, 2.2rem) !important; font-weight: 900 !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.6rem, 7vw, 2.3rem); margin-bottom: 20px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; padding: 15px !important; border-radius: 12px !important; }
        
        /* 🔗 실시간 확인 버튼 (김프 모드) */
        .stLinkButton > a {
            background-color: #31333f !important; color: #26A17B !important; 
            border: 1px solid #26A17B !important; border-radius: 5px !important;
            font-size: 0.75rem !important; font-weight: 700 !important; width: 100%; text-align: center;
        }
        
        /* 💹 매매 전용 버튼 스타일 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 10px; border: none; height: 3.5em; width: 100%; }
        
        /* ⚡ 퀵 수량 버튼 (100, 500 등) */
        .quick-btn-container div[data-testid="stHorizontalBlock"] button {
            background-color: #31333f !important; border: 1px solid #555 !important; font-size: 0.8rem !important; height: 2.5em !important;
        }

        .trade-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진
def fetch_safe(target):
    h = {'User-Agent': 'Mozilla/5.0'}
    try:
        if target == "up": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        if target == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
        if target == "ok": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        if target == "bn":
            try: return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", headers=h, timeout=2).json()['price'])
            except: return None
    except: return None

# 세션 초기화
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp',
                 'buy_q_input': 100.0, 'sell_q_input': 100.0, 'history': [], 'trade_logs': []}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_v36_style()

# 🛡️ 로그인 (잔상 방지)
main_placeholder = st.empty()
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Final System</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v36")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty(); time.sleep(0.15); st.rerun()
            else: st.error("열쇠 불일치")
        st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드
# ---------------------------------------------------------

# 상단 내비게이션
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 실시간 김프 & 거래소", key="nav_kimp"): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 가상 매매 터미널", key="nav_trade"): st.session_state['menu'] = "trade"

# 데이터 로드
up, bn, ok, ex = fetch_safe("up"), fetch_safe("bn"), fetch_safe("ok"), fetch_safe("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_list = [p for p in [bn_k, ok_k] if p]
global_avg = sum(avg_list)/len(avg_list) if avg_list else (up if up else 1)
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0
kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime('%H:%M:%S')

# [모드 1: 실시간 김프 & 거래소 직통]
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        st.link_button("실시간 확인 🔗", "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-USDT")
    with c2: 
        st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
        st.link_button("실시간 확인 🔗", "https://www.binance.com/en/trade/USDT_USD?type=spot")
    with c3: 
        st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
        st.link_button("실시간 확인 🔗", "https://www.okx.com/trade-spot/usdt-usd")
    with c4: 
        st.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
        st.caption(f"기준: {global_avg:,.0f}원")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    time.sleep(15); st.rerun()

# [모드 2: 가상 매매 (퀵 버튼 부활)]
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 지갑 상황
    pnl = (st.session_state['qty'] * up) - (st.session_state['qty'] * st.session_state['avg']) if (st.session_state['qty'] > 0 and up) else 0
    pnl_p = (pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0 and st.session_state['avg'] > 0) else 0
    
    v1, v2 = st.columns(2)
    with v1: st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📈 실시간 손익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_p:+.2f}%)</h2><p>현재가: {up:,.0f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    
    # 🛒 매수 섹션 (퀵 버튼 100, 500, 1000, 3000)
    st.subheader("🟢 수량 매수 (USDT)")
    bq1, bq2, bq3, bq4 = st.columns(4)
    if bq1.button("100", key="buy100"): st.session_state['buy_q_input'] = 100.0
    if bq2.button("500", key="buy500"): st.session_state['buy_q_input'] = 500.0
    if bq3.button("1000", key="buy1000"): st.session_state['buy_q_input'] = 1000.0
    if bq4.button("3000", key="buy3000"): st.session_state['buy_q_input'] = 3000.0
    
    buy_q = st.number_input("매수할 USDT 수량", value=st.session_state['buy_q_input'], step=10.0, key="buy_field")
    buy_cost = buy_q * up
    st.write(f"💰 결제 예정 금액: **{buy_cost:,.0f}원** (수수료 별도)")
    
    if st.button("🚀 즉시 매수 실행"):
        total_cost = buy_cost * 1.0005
        if st.session_state['cash'] >= total_cost:
            st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + buy_cost) / (st.session_state['qty'] + buy_q)
            st.session_state['qty'] += buy_q
            st.session_state['cash'] -= total_cost
            st.session_state['trade_logs'].append({"시간": now, "유형": "매수", "수량": buy_q, "단가": up})
            st.success("매수 성공!"); time.sleep(0.5); st.rerun()
        else: st.error("현금이 부족합니다!")

    st.write("---")
    
    # 💰 매도 섹션 (퀵 버튼)
    st.subheader("🔴 수량 매도 (USDT)")
    sq1, sq2, sq3, sq4 = st.columns(4)
    if sq1.button("100", key="sell100"): st.session_state['sell_q_input'] = 100.0
    if sq2.button("500", key="sell500"): st.session_state['sell_q_input'] = 500.0
    if sq3.button("1000", key="sell1000"): st.session_state['sell_q_input'] = 1000.0
    if sq4.button("3000", key="sell3000"): st.session_state['sell_q_input'] = 3000.0
    
    sell_q = st.number_input("매도할 USDT 수량", value=st.session_state['sell_q_input'], step=10.0, key="sell_field")
    sell_val = sell_q * up
    st.write(f"💵 회수 예정 금액: **{sell_val:,.0f}원**")
    
    if st.button("💰 즉시 매도 실행"):
        if st.session_state['qty'] >= sell_q:
            st.session_state['cash'] += (sell_val * 0.9995)
            st.session_state['qty'] -= sell_q
            if st.session_state['qty'] <= 0: st.session_state['avg'] = 0
            st.session_state['trade_logs'].append({"시간": now, "유형": "매도", "수량": sell_q, "단가": up})
            st.success("매도 성공!"); time.sleep(0.5); st.rerun()
        else: st.error("보유 수량이 부족합니다!")

with st.sidebar:
    if st.button("🚪 안전 로그아웃"): st.session_state['auth'] = False; st.rerun()
