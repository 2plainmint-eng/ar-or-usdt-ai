import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 관리자 공구함 제거 및 프리미엄 스타일
def apply_clean_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 🧹 상단바, 푸터, 관리 도구(연필, 깃허브) 숨기기 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        [data-testid="stToolbar"] {display: none !important;}
        
        /* 배경색 및 폰트 */
        .stApp { background-color: #0e1117 !important; }
        .main-title { 
            text-align: center; color: #26A17B !important; 
            font-weight: 700 !important; font-size: clamp(1.5rem, 6vw, 2.2rem); 
            margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        
        /* 카드 디자인 */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; border-top: 5px solid #26A17B !important;
        }
        [data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: clamp(1.8rem, 7vw, 2.8rem) !important; font-weight: 800 !important; }
        [data-testid="stMetricLabel"] p { color: #d1d1d1 !important; font-size: clamp(0.9rem, 4vw, 1.1rem) !important; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 [강화] 데이터 수집 엔진 (바이낸스 api3 사용)
def fetch_data(target):
    try:
        if target == "upbit":
            return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        elif target == "binance":
            # api3.binance.com이 외부 서버에서 가장 안정적입니다.
            return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        elif target == "okx":
            return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()['data'][0]['last'])
        elif target == "ex":
            return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except:
        return None

# 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_clean_style()

# 🛡️ 입구 검문소
placeholder = st.empty()
with placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([0.05, 0.9, 0.05])
        with col:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access</p></div>", unsafe_allow_html=True)
            pw = st.text_input("열쇠 (PW)", type="password", key="pw_v18")
            if st.button("시스템 접속"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    placeholder.empty()
                    time.sleep(0.1)
                    st.rerun()
                else: st.error("열쇠가 틀렸습니다.")
        st.stop()

# 📈 대시보드 메인
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
    menu = st.radio("메뉴 선택", ["🏠 실시간 김프", "💹 가상 매매 (Beta)", "📝 회원 관리"])
    st.write("---")
    if st.button("🚪 오두막 나가기"):
        st.session_state['auth'] = False
        st.rerun()

if menu == "🏠 실시간 김프":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    up = fetch_data("upbit")
    bn = fetch_data("binance")
    ok = fetch_data("okx")
    ex = fetch_data("ex")

    if up and ex:
        # 한화 변환
        bn_k = (bn * ex) if bn else None
        ok_k = (ok * ex) if ok else None
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기 중")
        with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기 중")
        
        st.write("---")
        avg_g = [p for p in [bn_k, ok_k] if p]
        if avg_g:
            k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100
            color = "normal" if k_val > 0 else "inverse"
            
            res1, res2 = st.columns(2)
            with res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
            with res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
            
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

elif menu == "💹 가상 매매 (Beta)":
    st.markdown("<h2 style='text-align:center;'>💹 가상 투자 연습장</h2>", unsafe_allow_html=True)
    st.info("아빠님, 이 공간은 유닛 737이 '가상 지갑'과 '매수/매도' 버튼을 설치하고 있는 중입니다. 곧 김프를 활용한 모의 투자가 가능해질 거예요!")

else:
    st.markdown("<h2 style='text-align:center;'>📝 회원 관리</h2>", unsafe_allow_html=True)
    st.write("이곳에서 Google 아이디로 가입한 회원들을 관리하실 수 있습니다.")
