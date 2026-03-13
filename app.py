import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 모바일 배지 박멸 및 고대비 스타일
def apply_ghost_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 [하단 배지 박멸] 왕관, 스트림릿 로고, 메뉴바 원천 차단 */
        header, footer, #MainMenu {visibility: hidden; display: none !important;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;} /* 모바일 하단 배지 전용 */
        div[class^="viewerBadge"] {display: none !important;}
        
        /* 전체 배경 및 폰트 */
        .stApp { background-color: #0e1117 !important; top: -50px; }
        .main-title { text-align: center; color: #26A17B !important; font-weight: 700; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 25px; }
        
        /* 지표 카드 및 가상 투자 섹션 디자인 */
        [data-testid="stMetric"] { background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important; border-top: 5px solid #26A17B !important; }
        .trading-card { background-color: #1e2129; padding: 25px; border-radius: 15px; border: 1px solid #333; margin-bottom: 20px; }
        
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

# 4. 🎰 [Beta] 가상 자산 초기화 (1,000만 원)
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0  # 가상 현금
if 'usdt_holdings' not in st.session_state: st.session_state['usdt_holdings'] = 0.0  # 보유 코인
if 'history' not in st.session_state: st.session_state['history'] = []

apply_ghost_clean_style()

# 🛡️ 입구 검문소
placeholder = st.empty()
with placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([0.05, 0.9, 0.05])
        with col:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private Solution</p></div>", unsafe_allow_html=True)
            user_id = st.text_input("아이디 (ID)", value="admin")
            user_pw = st.text_input("열쇠 (PW)", type="password")
            if st.button("시스템 접속"):
                if user_pw == "aror737":
                    st.session_state['auth'] = True
                    st.session_state['user_role'] = "admin" if user_id == "admin" else "user"
                    placeholder.empty()
                    time.sleep(0.15)
                    st.rerun()
                else: st.error("열쇠가 틀렸습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 대시보드 메인
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
    menu = st.radio("메뉴 선택", ["🏠 실시간 김프", "💹 가상 매매 (Beta)", "📝 회원 관리"] if st.session_state['user_role'] == 'admin' else ["🏠 실시간 김프", "💹 가상 매매 (Beta)"])
    st.write("---")
    st.metric("💰 내 가상 자산", f"{st.session_state['cash']:,.0f}원")
    if st.button("🚪 오두막 나가기"):
        st.session_state['auth'] = False
        st.rerun()

# 데이터 미리 수집
up, bn, ok, ex = fetch_data("upbit"), fetch_data("binance"), fetch_data("okx"), fetch_data("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_g = [p for p in [bn_k, ok_k] if p]
k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100 if (up and avg_g) else 0.0

# [1. 실시간 김프]
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
        if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
        time.sleep(12); st.rerun()

# [2. 가상 매매 Beta]
elif menu == "💹 가상 매매 (Beta)":
    st.markdown("<div class='main-title'>💹 가상 매매 터미널</div>", unsafe_allow_html=True)
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 💳 나의 지갑")
        st.write(f"**보유 현금:** {st.session_state['cash']:,.0f} KRW")
        st.write(f"**보유 USDT:** {st.session_state['usdt_holdings']:,.2f} USDT")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_v2:
        st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
        st.write("### 🛒 현재 가격 (업비트)")
        st.write(f"**1 USDT =** {up:,.0f} KRW")
        st.write(f"**현재 김프:** {k_val:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    trade_col1, trade_col2 = st.columns(2)
    with trade_col1:
        st.subheader("🟢 USDT 매수")
        amount_to_buy = st.number_input("매수할 원화 금액(KRW)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0)
        if st.button("풀매수 (Buy)"):
            if up > 0:
                bought_usdt = amount_to_buy / up
                st.session_state['cash'] -= amount_to_buy
                st.session_state['usdt_holdings'] += bought_usdt
                st.success(f"{amount_to_buy:,.0f}원 어치 매수 완료! ({bought_usdt:.2f} USDT 보유)")
                st.rerun()

    with trade_col2:
        st.subheader("🔴 USDT 매도")
        amount_to_sell = st.number_input("매도할 코인 수량(USDT)", min_value=0.0, max_value=st.session_state['usdt_holdings'], step=10.0)
        if st.button("전량 매도 (Sell)"):
            if up > 0:
                sold_krw = amount_to_sell * up
                st.session_state['cash'] += sold_krw
                st.session_state['usdt_holdings'] -= amount_to_sell
                st.success(f"{amount_to_sell:.2f} USDT 매도 완료! ({sold_krw:,.0f}원 회수)")
                st.rerun()

# [3. 회원 관리]
elif menu == "📝 회원 관리":
    st.markdown("<h2 style='text-align:center;'>📝 비밀 통제실</h2>", unsafe_allow_html=True)
    st.write("주인장 전용 관리 페이지입니다.")
