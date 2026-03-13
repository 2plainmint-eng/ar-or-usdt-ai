import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 실전 정산 UI 스타일
def apply_v39_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 설정 */
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.2rem, 5vw, 2.2rem) !important; font-weight: 900 !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.6rem, 7vw, 2.3rem); margin-bottom: 20px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; padding: 15px !important; border-radius: 12px !important; }
        
        /* 💹 일반 버튼 스타일 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 8px; border: none; height: 3.5em; width: 100%; }
        
        /* ⚡ 퀵 수량 버튼 스타일 */
        div[data-testid="stHorizontalBlock"] div.stButton > button {
            background-color: #31333f !important; border: 1px solid #555 !important; height: 2.5em !important; font-size: 0.9rem !important;
        }

        /* 🔥 전량 매매 전용 (빨간색 강조) */
        .full-btn div.stButton > button { background-color: #ff4b4b !important; border: none !important; }
        
        .trade-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
        .profit-warning { color: #ff4b4b; font-weight: 900; font-size: 1.1rem; border: 2px solid #ff4b4b; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진
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

# 4. 🎰 세션 관리 (데이터 및 버튼 상태 보존)
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp',
                 'trade_q_val': 100.0, 'history': [], 'trade_logs': []}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_v39_style()

# 🛡️ 로그인 (잔상 방지 플레이스홀더)
main_placeholder = st.empty()
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Pro Terminal</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v39_final")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty(); time.sleep(0.15); st.rerun()
            else: st.error("열쇠 불일치")
        st.stop()

# 📈 메인 대시보드
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 김프 검증", key="nav_kimp"): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 가상 매매", key="nav_trade"): st.session_state['menu'] = "trade"

# 실시간 데이터 로드
up, bn, ok, ex = fetch_safe("up"), fetch_safe("bn"), fetch_safe("ok"), fetch_safe("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_list = [p for p in [bn_k, ok_k] if p]
global_avg = sum(avg_list)/len(avg_list) if avg_list else (up if up else 1)
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0
kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime('%H:%M:%S')

# [모드 1: 실시간 김프]
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 실시간 검증</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원"); st.link_button("확인 🔗", "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-USDT")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기"); st.link_button("확인 🔗", "https://www.binance.com/en/trade/USDT_USD")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기"); st.link_button("확인 🔗", "https://www.okx.com/trade-spot/usdt-usd")
    with c4: st.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    time.sleep(15); st.rerun()

# [모드 2: 가상 매매 Pro]
else:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널 (Pro)</div>", unsafe_allow_html=True)
    
    # 💡 실시간 정산 시뮬레이션 (수수료 공제 후 진짜 수익)
    current_value = st.session_state['qty'] * up
    sell_fee = current_value * 0.0005
    estimated_net = current_value - sell_fee 
    total_invested = st.session_state['qty'] * st.session_state['avg']
    net_pnl = estimated_net - total_invested
    net_pnl_pct = (net_pnl / total_invested * 100) if total_invested > 0 else 0

    v1, v2 = st.columns(2)
    with v1: 
        st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if net_pnl > 0 else "#1c83e1" if net_pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📊 예상 정산 수익 (수수료 공제 후)</h3><h2 style='color:{p_color};'>{net_pnl:,.0f}원 ({net_pnl_pct:+.2f}%)</h2><p>현재가: {up:,.0f}원</p></div>", unsafe_allow_html=True)
        if (current_value - total_invested) > 0 and net_pnl < 0:
            st.markdown("<div class='profit-warning'>⚠️ 경고: 수수료를 떼면 마이너스입니다! 더 오를 때까지 대기하세요.</div>", unsafe_allow_html=True)

    st.write("---")
    
    # 🛒 매수 섹션 (퀵 수량 버튼 전선 연결)
    st.subheader("🛒 매수 실행 (USDT)")
    bq1, bq2, bq3, bq4 = st.columns(4)
    if bq1.button("100", key="buy_100"): st.session_state['trade_q_val'] = 100.0; st.rerun()
    if bq2.button("500", key="buy_500"): st.session_state['trade_q_val'] = 500.0; st.rerun()
    if bq3.button("1000", key="buy_1000"): st.session_state['trade_q_val'] = 1000.0; st.rerun()
    if bq4.button("3000", key="buy_3000"): st.session_state['trade_q_val'] = 3000.0; st.rerun()
    
    trade_q = st.number_input("거래 수량 입력", value=st.session_state['trade_q_val'], step=10.0, key="q_input")
    
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("🚀 즉시 매수"):
            cost = trade_q * up * 1.0005
            if st.session_state['cash'] >= cost:
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_q * up)) / (st.session_state['qty'] + trade_q)
                st.session_state['qty'] += trade_q; st.session_state['cash'] -= cost
                st.success("매수 성공!"); time.sleep(0.5); st.rerun()
            else: st.error("현금 부족")
    with c_b2:
        st.markdown("<div class='full-btn'>", unsafe_allow_html=True)
        if st.button("🔥 전량 매수 (ALL-IN)"):
            max_q = (st.session_state['cash'] / 1.0005) / up
            if max_q > 0.1:
                cost = max_q * up * 1.0005
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (max_q * up)) / (st.session_state['qty'] + max_q)
                st.session_state['qty'] += max_q; st.session_state['cash'] -= cost
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    
    # 💰 매도 섹션 (즉시 vs 전량 정산)
    st.subheader("💰 매도 실행 (USDT)")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        if st.button("💸 즉시 매도"):
            if st.session_state['qty'] >= trade_q:
                st.session_state['cash'] += (trade_q * up * 0.9995)
                st.session_state['qty'] -= trade_q
                if st.session_state['qty'] <= 0: st.session_state['avg'] = 0
                st.rerun()
            else: st.error("수량 부족")
    with c_s2:
        st.markdown("<div class='full-btn'>", unsafe_allow_html=True)
        if st.button("💎 전량 정산 (EXIT)"):
            if st.session_state['qty'] > 0:
                st.session_state['cash'] += (st.session_state['qty'] * up * 0.9995)
                st.session_state['qty'] = 0; st.session_state['avg'] = 0
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
