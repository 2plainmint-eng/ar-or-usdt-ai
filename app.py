import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 트레이딩 버튼 스타일
def apply_v34_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.4rem, 6vw, 2.5rem) !important; font-weight: 900 !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.6rem, 7vw, 2.3rem); margin-bottom: 20px; }
        .trade-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
        
        /* 매매 버튼 스타일 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 8px; border: none; }
        .quick-btn > div > div > button { background-color: #31333f !important; border: 1px solid #555 !important; font-size: 0.8rem !important; height: 2.5em !important; }
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

# 세션 관리 (자산 보존)
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp',
                 'realized_pnl': 0.0, 'total_fees': 0.0, 'wins': 0, 'losses': 0, 'history': [], 'trade_logs': []}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_v34_style()

# 🛡️ 로그인
main_area = st.empty()
if not st.session_state['auth']:
    with main_area.container():
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Terminal</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v34")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_area.empty(); time.sleep(0.15); st.rerun()
            else: st.error("열쇠 불일치")
    st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드
# ---------------------------------------------------------

# 상단 내비게이션
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 실시간 김프", key="nav_kimp"): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 가상 매매 & 분석", key="nav_trade"): st.session_state['menu'] = "trade"

# 데이터 로드
up, bn, ok, ex = fetch_safe("up"), fetch_safe("bn"), fetch_safe("ok"), fetch_safe("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_list = [p for p in [bn_k, ok_k] if p]
global_avg = sum(avg_list)/len(avg_list) if avg_list else (up if up else 1)
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0
kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime('%H:%M:%S')

if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
    with c4: st.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    time.sleep(15); st.rerun()

else:
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    
    # 지갑 및 실시간 손익
    cur_pnl = (st.session_state['qty'] * up) - (st.session_state['qty'] * st.session_state['avg']) if (st.session_state['qty'] > 0 and up) else 0
    pnl_p = (cur_pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0 and st.session_state['avg'] > 0) else 0
    
    v1, v2 = st.columns(2)
    with v1: st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if cur_pnl > 0 else "#1c83e1" if cur_pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📊 실시간 손익</h3><h2 style='color:{p_color};'>{cur_pnl:,.0f}원 ({pnl_p:+.2f}%)</h2><p>현재가: {up:,.0f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    
    # 🛒 [매수 영역]
    st.subheader("🟢 USDT 매수 (Buy)")
    if 'buy_qty' not in st.session_state: st.session_state['buy_qty'] = 100.0
    
    # 퀵 버튼
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("100", key="b100"): st.session_state['buy_qty'] = 100.0
    if q2.button("500", key="b500"): st.session_state['buy_qty'] = 500.0
    if q3.button("1000", key="b1000"): st.session_state['buy_qty'] = 1000.0
    if q4.button("3000", key="b3000"): st.session_state['buy_qty'] = 3000.0
    
    buy_q = st.number_input("매수 수량(USDT)", value=st.session_state['buy_qty'], step=10.0, key="buy_input")
    buy_cost = buy_q * up
    st.write(f"💰 예상 결제 금액: **{buy_cost:,.0f}원** (잔액: {st.session_state['cash']:,.0f}원)")
    
    if st.button("🚀 즉시 매수", key="buy_exec"):
        total_with_fee = buy_cost * 1.0005
        if st.session_state['cash'] >= total_with_fee:
            fee = buy_cost * 0.0005
            st.session_state['total_fees'] += fee
            st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + buy_cost) / (st.session_state['qty'] + buy_q)
            st.session_state['qty'] += buy_q
            st.session_state['cash'] -= total_with_fee
            st.session_state['trade_logs'].append({"시간": now, "유형": "매수", "수량": buy_q, "단가": up})
            st.success(f"{buy_q} USDT 매수 완료!"); time.sleep(0.5); st.rerun()
        else: st.error("현금이 부족합니다!")

    st.write("---")
    
    # 💰 [매도 영역]
    st.subheader("🔴 USDT 매도 (Sell)")
    if 'sell_qty' not in st.session_state: st.session_state['sell_qty'] = 100.0
    
    sq1, sq2, sq3, sq4 = st.columns(4)
    if sq1.button("100", key="s100"): st.session_state['sell_qty'] = 100.0
    if sq2.button("500", key="s500"): st.session_state['sell_qty'] = 500.0
    if sq3.button("1000", key="s1000"): st.session_state['sell_qty'] = 1000.0
    if sq4.button("3000", key="s3000"): st.session_state['sell_qty'] = 3000.0
    
    sell_q = st.number_input("매도 수량(USDT)", value=st.session_state['sell_qty'], step=10.0, key="sell_input")
    sell_revenue = sell_q * up
    st.write(f"💵 예상 회수 금액: **{sell_revenue:,.0f}원** (보유: {st.session_state['qty']:.2f} USDT)")
    
    if st.button("💰 즉시 매도", key="sell_exec"):
        if st.session_state['qty'] >= sell_q:
            fee = sell_revenue * 0.0005
            st.session_state['total_fees'] += fee
            
            # 수익 확정 계산
            trade_pnl = sell_revenue - fee - (sell_q * st.session_state['avg'])
            st.session_state['realized_pnl'] += trade_pnl
            if trade_pnl > 0: st.session_state['wins'] += 1
            else: st.session_state['losses'] += 1
            
            st.session_state['cash'] += (sell_revenue - fee)
            st.session_state['qty'] -= sell_q
            if st.session_state['qty'] <= 0: st.session_state['avg'] = 0
            st.session_state['trade_logs'].append({"시간": now, "유형": "매도", "수량": sell_q, "단가": up})
            st.success(f"{sell_q} USDT 매도 완료!"); time.sleep(0.5); st.rerun()
        else: st.error("보유 수량이 부족합니다!")

with st.sidebar:
    if st.button("🚪 안전 로그아웃"): st.session_state['auth'] = False; st.rerun()
