import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 [필수] 페이지 설정 (모바일 최적화 및 사이드바 기본 닫힘)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 보안 강화 딥 클리닝 스타일
def apply_deep_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 [보안 & 클린] 시스템 장식물 및 로고 싹 지우기 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* 왕관(Deploy) 및 하단 스트림릿 배지 완벽 차단 */
        .stAppDeployButton {display:none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        
        /* 전체 배경 및 시인성 강화 */
        .stApp { background-color: #0e1117 !important; top: -50px; }
        .main-title { text-align: center; color: #26A17B !important; font-weight: 700 !important; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 25px; }
        
        /* 지표 카드 스타일 (고대비) */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; border-top: 5px solid #26A17B !important;
        }
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.8rem, 7vw, 2.8rem) !important; font-weight: 800 !important; }
        
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

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = "user"
if 'history' not in st.session_state: st.session_state['history'] = []

apply_deep_clean_style()

# 🛡️ [입구] 보안 로그인 창
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
                    time.sleep(0.15) # 아빠님의 타이밍 묘수
                    st.rerun()
                else: st.error("열쇠가 틀렸습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 대시보드 메인
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
    menu_options = ["🏠 실시간 김프", "💹 가상 매매 (Beta)"]
    if st.session_state['user_role'] == "admin": menu_options.append("📝 회원 관리")
    
    menu = st.radio("메뉴 선택", menu_options)
    st.write("---")
    st.info(f"접속: {'주인장' if st.session_state['user_role'] == 'admin' else '일반 회원'}")
    if st.button("🚪 오두막 나가기"):
        st.session_state['auth'] = False
        st.rerun()

# [실시간 김프 화면]
if menu == "🏠 실시간 김프":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    up, bn, ok, ex = fetch_data("upbit"), fetch_data("binance"), fetch_data("okx"), fetch_data("ex")

    if up and ex:
        bn_k = (bn * ex) if bn else None
        ok_k = (ok * ex) if ok else None
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
        with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
        
        st.write("---")
        avg_g = [p for p in [bn_k, ok_k] if p]
        if avg_g:
            k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100
            ck1, ck2 = st.columns(2)
            with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
            with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
            
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst).strftime('%H:%M:%S')
            st.session_state['history'].append({"시간": now, "김프": k_val})
            if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
            st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
        
        st.caption(f"최근 업데이트: {now}")
        time.sleep(12)
        st.rerun()

# [회원 관리 - 주인장 전용]
elif menu == "📝 회원 관리":
    st.markdown("<h2 style='text-align:center;'>📝 비밀 통제실</h2>", unsafe_allow_html=True)
    st.write("주인장님, 여기서 오두막의 보안 설정을 관리하실 수 있습니다.")
