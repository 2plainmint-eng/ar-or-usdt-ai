import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="expanded")

# 2. 🎨 [디자인] 고대비 & 모바일 최적화 (글자색 강제 고정)
def apply_super_contrast_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        
        /* 🧹 시스템 UI 싹 지우기 */
        header, footer, #MainMenu {visibility: hidden; display: none !important;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stStatusWidget"], [data-testid="stDecoration"], .viewerBadge_container__1QSob {display: none !important;}
        
        /* 💡 글자 시인성 폭발 (핵심 해결책) */
        .stApp { background-color: #0e1117 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 (강제 흰색) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important; 
            -webkit-text-fill-color: #ffffff !important;
            font-size: clamp(1.8rem, 8vw, 3rem) !important;
            font-weight: 900 !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        }
        
        /* 지표 라벨 (강제 밝은 회색) */
        [data-testid="stMetricLabel"] p {
            color: #e0e0e0 !important;
            -webkit-text-fill-color: #e0e0e0 !important;
            font-size: clamp(0.9rem, 4vw, 1.2rem) !important;
            font-weight: 700 !important;
        }

        /* 탭 디자인 (모바일 메뉴) */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e2129; border-radius: 10px; padding: 10px 20px; color: white !important;
        }
        
        /* 제목 및 카드 */
        .main-title { text-align: center; color: #26A17B !important; font-size: clamp(1.5rem, 6vw, 2.2rem); font-weight: 700; margin-bottom: 25px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 5px solid #26A17B !important; }
        .trading-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 15px; }

        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; border-radius: 10px; font-weight: 700; height: 3.8em; border: none; }
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

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'holdings' not in st.session_state: st.session_state['holdings'] = 0.0
if 'avg_price' not in st.session_state: st.session_state['avg_price'] = 0.0
if 'history' not in st.session_state: st.session_state['history'] = []

apply_super_contrast_style()

# 🛡️ 로그인 창
placeholder = st.empty()
with placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([0.05, 0.9, 0.05])
        with col:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private Terminal</p></div>", unsafe_allow_html=True)
            user_pw = st.text_input("열쇠 (PW)", type="password")
            if st.button("시스템 접속"):
                if user_pw == "aror737":
                    st.session_state['auth'] = True
                    placeholder.empty(); time.sleep(0.1); st.rerun()
                else: st.error("열쇠 불일치")
        st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드 (탭 메뉴 도입)
# ---------------------------------------------------------

# 데이터 수집
up = fetch_data("upbit"); bn = fetch_data("binance"); ok = fetch_data("okx"); ex = fetch_data("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_g = [p for p in [bn_k, ok_k] if p]
k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100 if (up and avg_g) else 0.0

# 상단 탭 (모바일에서 사이드바 안 열어도 되게 함)
tab_home, tab_trade, tab_admin = st.tabs(["🏠 실시간 김프", "💹 가상 매매", "📝 관리자"])

# [탭 1: 실시간 김프]
with tab_home:
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    if up and ex:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
        with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
        
        st.write("---")
        ck1, ck2 = st.columns(2)
        with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
        with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
        time.sleep(12); st.rerun()

# [탭 2: 가상 매매]
with tab_trade:
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    pnl = (st.session_state['holdings'] * up) - (st.session_state['holdings'] * st.session_state['avg_price']) if st.session_state['holdings'] > 0 else 0
    pnl_pct = (pnl / (st.session_state['holdings'] * st.session_state['avg_price']) * 100) if (st.session_state['holdings'] > 0 and st.session_state['avg_price'] > 0) else 0

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 💳 나의 지갑")
        st.write(f"💵 **현금:** {st.session_state['cash']:,.0f} KRW")
        st.write(f"🪙 **수량:** {st.session_state['holdings']:.2f} USDT")
        st.write(f"📍 **평단:** {st.session_state['avg_price']:,.0f} KRW")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_v2:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 📈 수익률")
        p_color = "#ff4b4b" if pnl > 0 else "#31333f" if pnl == 0 else "#1c83e1"
        st.markdown(f"<h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_pct:.2f}%)</h2>", unsafe_allow_html=True)
        st.write(f"**현재가:** {up:,.0f}원")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    tc1, tc2 = st.columns(2)
    with tc1:
        st.subheader("🟢 매수")
        amt = st.number_input("매수금액(KRW)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0)
        if st.button("풀매수"):
            if up > 0 and amt > 0:
                new_q = amt / up
                st.session_state['avg_price'] = ((st.session_state['holdings'] * st.session_state['avg_price']) + (new_q * up)) / (st.session_state['holdings'] + new_q)
                st.session_state['holdings'] += new_q
                st.session_state['cash'] -= amt
                st.rerun()

    with tc2:
        st.subheader("🔴 매도")
        qty = st.number_input("매도수량(USDT)", min_value=0.0, max_value=st.session_state['holdings'], step=10.0)
        if st.button("전량매도"):
            if up > 0 and qty > 0:
                st.session_state['cash'] += (qty * up)
                st.session_state['holdings'] -= qty
                if st.session_state['holdings'] == 0: st.session_state['avg_price'] = 0
                st.rerun()

# [탭 3: 관리자]
with tab_admin:
    st.markdown("<h2 style='text-align:center;'>📝 통제실</h2>", unsafe_allow_html=True)
    if st.button("🚪 안전 로그아웃"):
        st.session_state['auth'] = False; st.rerun()
