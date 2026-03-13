import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 공구함 숨기기 및 프리미엄 스타일
def apply_final_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 [옥에 티 제거] 연필, 깃허브 아이콘 등 상단바 싹 제거 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        
        /* 전체 배경 및 폰트 */
        .stApp { background-color: #0e1117 !important; }
        .main-title { 
            text-align: center; color: #26A17B !important; 
            font-weight: 700 !important; font-size: clamp(1.5rem, 6vw, 2.2rem); 
            margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        
        /* 지표 카드 스타일 */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; border-top: 5px solid #26A17B !important;
        }
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.8rem, 7vw, 2.8rem) !important; font-weight: 800 !important; }
        [data-testid="stMetricLabel"] p { color: #d1d1d1 !important; font-size: clamp(0.9rem, 4vw, 1.1rem) !important; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.8em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 [엔진 보강] 바이낸스 전용 통로 추가
def get_price_robust(exchange):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if exchange == "upbit":
            return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        elif exchange == "binance":
            # api3가 클라우드 서버에서 가장 응답이 빠릅니다
            return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=3).json()['price'])
        elif exchange == "okx":
            return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        elif exchange == "ex":
            return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
    except:
        return None

# 초기 상태
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_final_clean_style()

# 🛡️ 입구 검문소
placeholder = st.empty()
with placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.05, 0.9, 0.05])
        with col_login:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access Only</p></div>", unsafe_allow_html=True)
            pw = st.text_input("열쇠 (PW)", type="password", key="pw_v17")
            if st.button("시스템 접속", key="btn_v17"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    placeholder.empty()
                    time.sleep(0.15)
                    st.rerun()
                else: st.error("열쇠가 틀렸습니다.")
        st.stop()

# 📈 대시보드 메인
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ MENU</h2>", unsafe_allow_html=True)
    st.write(f"접속: 아르 아빠님")
    if st.button("🚪 오두막 나가기"):
        st.session_state['auth'] = False
        st.rerun()

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 실시간 낚시 시작
up = get_price_robust("upbit")
bn = get_price_robust("binance")
ok = get_price_robust("okx")
ex = get_price_robust("ex")

if up and ex:
    bn_k = (bn * ex) if bn else None
    ok_k = (ok * ex) if ok) else None
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "연결 재시도 중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "연결 재시도 중")
    
    st.write("---")
    
    # 김프 계산
    avg_g = [p for p in [bn_k, ok_k] if p]
    if avg_g:
        k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        ck1, ck2 = st.columns(2)
        with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
        
        st.subheader("📉 최근 변화 추이")
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    st.caption(f"최근 갱신: {now} (12초 자동 갱신)")
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 유닛 737이 심해에서 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
