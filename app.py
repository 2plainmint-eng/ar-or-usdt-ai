import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 [필수] 페이지 설정 및 클린 UI 선언
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 클린 인테리어 & 초고대비 스타일
def apply_clean_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 [옥에 티 제거] 관리자 도구 및 푸터 싹 지우기 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none !important;}
        .stApp { top: -45px; } /* 상단 여백 제거 */
        
        /* 기본 배경 및 폰트 */
        .stApp { background-color: #0e1117 !important; }
        .main-title, h1, h2, h3, .stSubheader { 
            text-align: center; color: #ffffff !important; font-weight: 700 !important; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        .main-title { color: #26A17B !important; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 25px; }
        
        /* 지표 카드 스타일 (고대비) */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; border: 1px solid #333 !important; border-top: 5px solid #26A17B !important;
        }
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.8rem, 7vw, 2.8rem) !important; font-weight: 800 !important; }
        [data-testid="stMetricLabel"] p { color: #d1d1d1 !important; font-size: clamp(0.9rem, 4vw, 1.1rem) !important; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 12px; font-weight: 700; width: 100%; height: 4em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_clean_premium_style()

# 🛡️ [잔상 방지] 아빠님 솔루션 적용
main_placeholder = st.empty()

with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.05, 0.9, 0.05])
        with col_login:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Terminal</p></div>", unsafe_allow_html=True)
            pw = st.text_input("오두막 열쇠 (PW)", type="password", key="pw_v15")
            if st.button("시스템 접속", key="btn_v15"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    main_placeholder.empty()
                    time.sleep(0.15)
                    st.rerun()
                else: st.error("열쇠가 맞지 않습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 클린 UI 버전
# ---------------------------------------------------------

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 데이터 수집
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    st.write("---")
    avg_g = [p for p in [bn_k, ok_k] if p]
    if avg_g:
        k_val = ((up_k / (sum(avg_g)/len(avg_g))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        ck1, ck2 = st.columns(2)
        with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 한국 시간 보정
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['history']) > 25: st.session_state['history'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    st.caption(f"최근 갱신: {now} (12초 자동 갱신)")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("로그아웃"):
            st.session_state['auth'] = False
            st.rerun()
            
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
