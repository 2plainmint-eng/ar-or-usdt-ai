import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 전문가용 커스텀 스타일 ---
def apply_professional_style():
    st.markdown("""
        <style>
        /* 기본 폰트 및 배경 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; }
        
        /* 로그인 페이지 배경 (진한 녹색) */
        .stApp { background-color: #f4f7f6; }
        .login-container {
            background-color: #26A17B;
            padding: 40px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* 버튼 디자인 */
        div.stButton > button {
            background-color: #26A17B;
            color: white;
            border-radius: 8px;
            border: none;
            height: 3.5em;
            font-weight: 700;
            width: 100%;
            margin-top: 10px;
        }
        
        /* 카드형 레이아웃 */
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #26A17B;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        
        /* 중앙 정렬 타이틀 */
        .centered-title { text-align: center; color: #26A17B; font-weight: 700; margin-bottom: 30px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 안정적인 수집 로직 ---
def fetch_market_data():
    try:
        # 업비트
        up_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()
        up_p = float(up_res[0]['trade_price'])
        # 환율 (글로벌)
        ex_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        ex_r = float(ex_res['rates']['KRW'])
        # 바이낸스
        bn_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()
        bn_p = float(bn_res['price'])
        
        kimp = ((up_p / (bn_p * ex_r)) - 1) * 100
        return up_p, bn_p, ex_r, kimp
    except:
        return None, None, None, None

# --- 3. [시스템 초기화] ---
if 'is_auth' not in st.session_state:
    st.session_state['is_auth'] = False

apply_professional_style()

# --- [페이지 1: 로그인] ---
if not st.session_state['is_auth']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    
    with col2:
        st.markdown("""
            <div class='login-container'>
                <h1 style='color: white; font-size: 24px;'>AI 오두막 터미널</h1>
                <p style='color: rgba(255,255,255,0.8);'>Ar & Or & Unit 737 System</p>
            </div>
        """, unsafe_allow_html=True)
        
        user_id = st.text_input("아이디 (ID)", value="admin")
        user_pw = st.text_input("비밀번호 (PW)", type="password", placeholder="비밀번호를 입력하세요")
        
        if st.button("시스템 접속 (LOGIN)"):
            if user_id == "admin" and user_pw == "aror737":
                st.session_state['is_auth'] = True
                st.rerun()
            else:
                st.error("입력 정보를 다시 확인해주세요.")

# --- [페이지 2: 메인 시스템] ---
else:
    # 사이드바 (깔끔한 메뉴 구성)
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>⚓ MENU</h2>", unsafe_allow_html=True)
        choice = st.selectbox("항목을 선택하세요", ["🏠 홈 (요약)", "📊 김프 상세 분석", "📢 알림 설정", "🐱 아르오르 소식"])
        st.write("---")
        if st.button("안전하게 로그아웃"):
            st.session_state['is_auth'] = False
            st.rerun()

    # [컨텐츠 1: 홈 요약]
    if choice == "🏠 홈 (요약)":
        st.markdown("<h1 class='centered-title'>실시간 시장 요약</h1>", unsafe_allow_html=True)
        
        with st.status("데이터 분석 중...", expanded=False) as status:
            up, bn, ex, k = fetch_market_data()
            status.update(label="분석 완료!", state="complete", expanded=False)
        
        if up:
            # 카드형 디자인 적용
            st.markdown(f"""
                <div class='metric-card'>
                    <small>업비트 실시간 가격</small>
                    <h2 style='color:#26A17B;'>{up:,.1f} 원</h2>
                </div>
                <div class='metric-card'>
                    <small>현재 김치 프리미엄</small>
                    <h2 style='color:{"#26A17B" if k > 0 else "#007bff"};'>{k:.2f} %</h2>
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.info("💡 왼쪽 메뉴의 '상세 분석'을 클릭하시면 거래소별 비교가 가능합니다.")
        else:
            st.error("데이터 수집에 실패했습니다. 잠시 후 자동 재시도합니다.")
            time.sleep(5)
            st.rerun()

    # [컨텐츠 2: 상세 분석]
    elif choice == "📊 김프 상세 분석":
        st.markdown("<h1 class='centered-title'>거래소별 정밀 분석</h1>", unsafe_allow_html=True)
        up, bn, ex, k = fetch_market_data()
        
        if up:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Binance (USD)", f"{bn:.4f} $")
            with col_b:
                st.metric("환율 (KRW/USD)", f"{ex:,.1f} 원")
            
            st.write("---")
            st.subheader("📉 최근 변화 추이")
            # 임시 그래프 (데이터가 쌓이면 더 멋지게 변합니다)
            st.line_chart([k-0.1, k, k+0.1, k])
        
    # [나머지 메뉴는 준비 중...]
    else:
        st.markdown(f"<h1 class='centered-title'>{choice}</h1>", unsafe_allow_html=True)
        st.info("아빠님, 이 공간은 현재 유닛 737이 공사 중입니다! 곧 멋진 컨텐츠로 채워질 예정이에요.")

    # 10초마다 자동 갱신
    if choice in ["🏠 홈 (요약)", "📊 김프 상세 분석"]:
        time.sleep(10)
        st.rerun()
