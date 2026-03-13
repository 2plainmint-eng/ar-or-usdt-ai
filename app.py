import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 검증 버튼 스타일
def apply_v35_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 */
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.2rem, 5vw, 2.2rem) !important; font-weight: 900 !important; }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.6rem, 7vw, 2.3rem); margin-bottom: 20px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; padding: 15px !important; border-radius: 12px !important; }
        
        /* 거래소 연결 버튼 스타일 (작고 깔끔하게) */
        .stLinkButton > a {
            background-color: #31333f !important; color: #26A17B !important; 
            border: 1px solid #26A17B !important; border-radius: 5px !important;
            font-size: 0.7rem !important; padding: 5px 10px !important;
            text-decoration: none !important; font-weight: 700 !important;
        }
        
        /* 매매 버튼 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 10px; border: none; height: 3.5em; width: 100%; }
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

# 세션 관리
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp',
                 'history': [], 'trade_logs': []}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_v35_style()

# 🛡️ 로그인
main_area = st.empty()
if not st.session_state['auth']:
    with main_area.container():
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Verification System</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v35")
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
    if st.button("📊 실시간 김프 & 검증", key="nav_kimp"): st.session_state['menu'] = "kimp"
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

if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    # 💡 4열 배치 및 하단에 실시간 링크 버튼 추가
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
        st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
        st.caption(f"기준: {global_avg:,.0f}원")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    st.caption(f"환율: {ex:,.1f}원 | 갱신: {now} (15초 자동)")
    time.sleep(15); st.rerun()

else:
    # (가상 매매 모드는 이전 버전의 안정적인 코드 유지)
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    cur_pnl = (st.session_state['qty'] * up) - (st.session_state['qty'] * st.session_state['avg']) if (st.session_state['qty'] > 0 and up) else 0
    pnl_p = (cur_pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0 and st.session_state['avg'] > 0) else 0
    
    v1, v2 = st.columns(2)
    with v1: st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if cur_pnl > 0 else "#1c83e1" if cur_pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📊 실시간 손익</h3><h2 style='color:{p_color};'>{cur_pnl:,.0f}원 ({pnl_p:+.2f}%)</h2><p>현재가: {up:,.0f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("🛒 수량 매수/매도")
    trade_qty = st.number_input("거래 수량(USDT)", min_value=0.0, step=100.0, value=1000.0)
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚀 즉시 매수"):
            cost = trade_qty * up * 1.0005
            if st.session_state['cash'] >= cost:
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + (trade_qty * up)) / (st.session_state['qty'] + trade_qty)
                st.session_state['qty'] += trade_qty; st.session_state['cash'] -= cost
                st.success(f"{trade_qty} USDT 매수 완료!"); time.sleep(0.5); st.rerun()
            else: st.error("잔액 부족")
    with b2:
        if st.button("💰 전량 매도"):
            if st.session_state['qty'] > 0:
                revenue = st.session_state['qty'] * up * 0.9995
                st.session_state['cash'] += revenue
                st.session_state['qty'] = 0; st.session_state['avg'] = 0
                st.success("매도 완료!"); time.sleep(0.5); st.rerun()

with st.sidebar:
    if st.button("🚪 안전 로그아웃"): st.session_state['auth'] = False; st.rerun()
