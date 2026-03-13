import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 모바일 하단 배지 핵폭탄 클리닝
def apply_nuclear_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 [하단 배지 원천 봉쇄] 모바일 아래쪽의 모든 로고와 버튼 숨기기 */
        header, footer, #MainMenu {visibility: hidden; display: none !important;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* 모바일 하단 배지(왕관, 로고) 타겟팅 공격 */
        div[class^="viewerBadge"], div[class*="viewerBadge"], .viewerBadge_container__1QSob {display: none !important;}
        footer {display: none !important;}
        
        /* 전체 배경 및 폰트 */
        .stApp { background-color: #0e1117 !important; top: -50px; }
        .main-title { text-align: center; color: #26A17B !important; font-weight: 700; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 25px; }
        
        /* 카드 디자인 */
        [data-testid="stMetric"] { background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important; border-top: 5px solid #26A17B !important; }
        .trading-card { background-color: #1e2129; padding: 25px; border-radius: 15px; border: 1px solid #333; margin-bottom: 20px; color: white; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진
def fetch_data(target):
    try:
        if target == "upbit": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        elif target == "binance": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        elif target == "okx": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()['data'][0]['last'])
        elif target == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except: return None

# 4. 🎰 가상 투자 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'holdings' not in st.session_state: st.session_state['holdings'] = 0.0
if 'avg_price' not in st.session_state: st.session_state['avg_price'] = 0.0
if 'history' not in st.session_state: st.session_state['history'] = []

apply_nuclear_clean_style()

# 🛡️ 입구 검문소
placeholder = st.empty()
with placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([0.05, 0.9, 0.05])
        with col:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Terminal</p></div>", unsafe_allow_html=True)
            user_pw = st.text_input("열쇠 (PW)", type="password", key="pw_v22")
            if st.button("시스템 접속"):
                if user_pw == "aror737":
                    st.session_state['auth'] = True
                    placeholder.empty(); time.sleep(0.15); st.rerun()
                else: st.error("열쇠가 틀렸습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 대시보드 로직
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
    menu = st.radio("메뉴 선택", ["🏠 실시간 김프", "💹 가상 매매 (Beta)", "📝 회원 관리"])
    st.write("---")
    # 사이드바에서 내 자산 바로보기
    st.metric("💰 가상 자산 총액", f"{st.session_state['cash'] + (st.session_state['holdings'] * fetch_data('upbit') if st.session_state['holdings'] > 0 else 0):,.0f}원")
    if st.button("🚪 로그아웃"):
        st.session_state['auth'] = False; st.rerun()

# 데이터 로드
up = fetch_data("upbit"); bn = fetch_data("binance"); ok = fetch_data("okx"); ex = fetch_data("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_g = [p for p in [bn_k, ok_k] if p]
k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100 if (up and avg_g) else 0.0

# [메뉴 1: 실시간 김프]
if menu == "🏠 실시간 김프":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    if up and ex:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
        with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
        
        st.write("---")
        ck1, ck2 = st.columns(2)
        with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
        with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['history']) > 25: st.session_state['history'].pop(0)
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
        time.sleep(12); st.rerun()

# [메뉴 2: 가상 매매 고도화]
elif menu == "💹 가상 매매 (Beta)":
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    # 수익률 계산
    current_val = st.session_state['holdings'] * up
    pnl = current_val - (st.session_state['holdings'] * st.session_state['avg_price']) if st.session_state['holdings'] > 0 else 0
    pnl_pct = (pnl / (st.session_state['holdings'] * st.session_state['avg_price']) * 100) if (st.session_state['holdings'] > 0 and st.session_state['avg_price'] > 0) else 0

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 💳 나의 지갑")
        st.write(f"💵 **가용 현금:** {st.session_state['cash']:,.0f} KRW")
        st.write(f"🪙 **보유 수량:** {st.session_state['holdings']:.2f} USDT")
        st.write(f"📍 **평균 단가:** {st.session_state['avg_price']:,.0f} KRW")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_v2:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 📈 투자 손익")
        color = "red" if pnl > 0 else "blue" if pnl < 0 else "white"
        st.markdown(f"**실시간 수익:** <span style='color:{color}; font-size:1.2rem; font-weight:bold;'>{pnl:,.0f} KRW ({pnl_pct:.2f}%)</span>", unsafe_allow_html=True)
        st.write(f"**현재가:** {up:,.0f} KRW")
        st.write(f"**김프:** {k_val:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    trade_col1, trade_col2 = st.columns(2)
    with trade_col1:
        st.subheader("🟢 USDT 매수")
        amount = st.number_input("매수 금액(KRW)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0)
        if st.button("풀매수 (Buy)"):
            if up > 0 and amount > 0:
                new_qty = amount / up
                # 평균단가 계산 공식: $$Avg = \frac{(OldQty \times OldAvg) + (NewQty \times CurrentPrice)}{OldQty + NewQty}$$
                total_qty = st.session_state['holdings'] + new_qty
                st.session_state['avg_price'] = ((st.session_state['holdings'] * st.session_state['avg_price']) + (new_qty * up)) / total_qty
                st.session_state['holdings'] = total_qty
                st.session_state['cash'] -= amount
                st.success(f"{amount:,.0f}원 매수 완료!"); st.rerun()

    with trade_col2:
        st.subheader("🔴 USDT 매도")
        qty = st.number_input("매도 수량(USDT)", min_value=0.0, max_value=st.session_state['holdings'], step=10.0)
        if st.button("전량 매도 (Sell)"):
            if up > 0 and qty > 0:
                gain = qty * up
                st.session_state['cash'] += gain
                st.session_state['holdings'] -= qty
                if st.session_state['holdings'] == 0: st.session_state['avg_price'] = 0
                st.success(f"{gain:,.0f}원 매도 완료!"); st.rerun()

# [메뉴 3: 회원 관리]
elif menu == "📝 회원 관리":
    st.markdown("<h2 style='text-align:center;'>📝 비밀 통제실</h2>", unsafe_allow_html=True)
    st.write("주인장 전용 관리 페이지입니다.")
