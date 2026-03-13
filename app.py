import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정 (상단 메뉴 복구를 위해 visibility 제거)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 프리미엄 스타일 (로그인/회원가입 강화)
def apply_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 전체 배경 */
        .stApp { background-color: #0e1117 !important; }
        
        /* 제목 디자인 */
        .main-title { 
            text-align: center; color: #26A17B !important; 
            font-weight: 700 !important; font-size: clamp(1.5rem, 6vw, 2.2rem); 
            margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        
        /* 로그인 카드 디자인 */
        .login-card { 
            background-color: #26A17B; padding: 35px 20px; 
            border-radius: 20px; color: white; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        
        /* 구글 로그인 버튼 스타일 */
        .google-btn {
            background-color: white; color: #444; border-radius: 10px;
            padding: 12px; font-weight: 700; display: flex; align-items: center;
            justify-content: center; cursor: pointer; margin-top: 15px;
            border: 1px solid #ddd; text-decoration: none;
        }

        /* 지표 카드 스타일 */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important; padding: 20px !important; border-radius: 15px !important;
            border-top: 5px solid #26A17B !important;
        }
        
        /* 버튼 공통 디자인 */
        div.stButton > button { 
            background-color: #26A17B; color: white; border-radius: 10px; 
            font-weight: 700; width: 100%; height: 3.8em; border: none;
        }
        
        /* 사이드바 로그아웃 버튼 전용 */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: #d9534f; /* 빨간색 계열 */
        }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 낚시 엔진
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_premium_style()

# 🛡️ [입구 검문소] 로그인 및 회원가입
main_placeholder = st.empty()

with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.05, 0.9, 0.05])
        with col_login:
            st.markdown("""
                <div class='login-card'>
                    <h1 style='color:white; margin-bottom:5px;'>AI 오두막</h1>
                    <p style='color:rgba(255,255,255,0.8);'>Ar & Or & Unit 737 Terminal</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 탭을 사용하여 로그인과 회원가입 분리
            tab1, tab2 = st.tabs(["🔐 로그인", "📝 회원가입"])
            
            with tab1:
                pw = st.text_input("열쇠 (Password)", type="password", key="login_pw")
                if st.button("시스템 입장하기", key="login_btn"):
                    if pw == "aror737":
                        st.session_state['auth'] = True
                        main_placeholder.empty()
                        time.sleep(0.15)
                        st.rerun()
                    else: st.error("열쇠가 맞지 않습니다.")
                
                st.markdown("<p style='text-align:center; color:gray; margin:10px 0;'>또는</p>", unsafe_allow_html=True)
                # 구글 로그인 (디자인 버튼)
                if st.button("🌐 Google 아이디로 시작하기", key="google_login"):
                    st.info("구글 OAuth 연동 설정이 필요합니다. (아빠님, API 키를 준비해주세요!)")

            with tab2:
                st.write("새로운 오두막 가족이 되시겠어요?")
                st.text_input("사용할 아이디")
                st.text_input("사용할 이메일")
                if st.button("회원가입 신청"):
                    st.success("신청이 완료되었습니다. 관리자 승인을 기다려주세요!")

        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 메인 페이지 (출구 포함)
# ---------------------------------------------------------

# 사이드바 (나가기 버튼 배치)
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
    st.info(f"접속 중: 아르 아빠님")
    st.write("---")
    if st.button("🚪 오두막 나가기 (Logout)"):
        st.session_state['auth'] = False
        st.rerun()

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
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['history']) > 25: st.session_state['history'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    
    st.caption(f"최근 갱신: {now} (12초 자동 갱신)")
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
