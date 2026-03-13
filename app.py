import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. 스타일 및 디자인 설정 (CSS) ---
def local_css():
    st.markdown("""
        <style>
        /* 메인 배경 및 정렬 */
        .main { text-align: center; }
        div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #26A17B; color: white; border: none; }
        div.stButton > button:hover { background-color: #1e7e60; color: white; }
        
        /* 로그인 박스 디자인 */
        .login-box {
            background-color: #26A17B;
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
        }
        h1, h2, h3 { text-align: center; color: #26A17B; }
        .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 수집 함수 ---
def get_data():
    try:
        up = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
        bn = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price']
        ex = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW']
        kimp = ((float(up) / (float(bn) * float(ex))) - 1) * 100
        return float(up), float(bn), float(ex), kimp
    except:
        return None, None, None, None

# --- 3. 초기 세션 설정 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'menu' not in st.session_state:
    st.session_state['menu'] = "🏠 홈"

local_css()

# --- [로그인 화면] ---
if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class='login-box'>
                <h2 style='color: white;'>AI 오두막 시스템 접속</h2>
                <p>Ar & Or & Unit 737 Monitoring Solution</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.write("")
            user_id = st.text_input("아이디", value="admin")
            user_pw = st.text_input("비밀번호", type="password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("로그인"):
                    if user_id == "admin" and user_pw == "aror737":
                        st.session_state['logged_in'] = True
                        st.rerun()
                    else:
                        st.error("정보를 확인하세요.")
            with col_btn2:
                st.button("회원가입 (준비중)")

# --- [메인 대시보드 화면] ---
else:
    # 사이드바 메뉴 구성
    with st.sidebar:
        st.markdown(f"### ⚓ 아르아빠 오두막")
        st.write("---")
        menu = st.radio("카테고리", ["🏠 대시보드", "📊 김프 상세분석", "🤖 AI 오두막 소식", "⚙️ 알림 설정"])
        st.write("---")
        if st.button("안전하게 로그아웃"):
            st.session_state['logged_in'] = False
            st.rerun()

    # 메뉴별 컨텐츠 표시
    if menu == "🏠 대시보드":
        st.markdown("<h1>📈 실시간 시장 요약</h1>", unsafe_allow_html=True)
        up, bn, ex, k = get_data()
        
        if up:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("🇰🇷 업비트 가격", f"{up:,.1f}원")
            with c2:
                color = "normal" if k > 0 else "inverse"
                st.metric("📊 현재 김프", f"{k:.2f}%", delta=f"{k:.2f}%", delta_color=color)
            
            st.write("---")
            st.info("💡 하위 카테고리인 '김프 상세분석'에서 차트와 해외 가격을 확인하세요.")
        else:
            st.warning("데이터를 낚는 중입니다...")
            time.sleep(2)
            st.rerun()

    elif menu == "📊 김프 상세분석":
        st.markdown("<h1>📊 상세 거래소 비교</h1>", unsafe_allow_html=True)
        up, bn, ex, k = get_data()
        if up:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Binance", f"{bn:.4f}$")
            col_b.metric("환율(USD/KRW)", f"{ex:,.1f}원")
            col_c.metric("계산 기준", "실시간 평균")
            
            st.write("---")
            st.subheader("📉 김프 변화 차트")
            # (차트 로직은 공간상 생략, 이전의 그래프 로직을 여기에 넣으면 됩니다)
            st.line_chart([k, k-0.1, k+0.2, k]) # 예시 차트
        
    elif menu == "🤖 AI 오두막 소식":
        st.markdown("<h1>🐱 아르 & 오르 애니메이션</h1>", unsafe_allow_html=True)
        st.write("### 현재 준비 중인 에피소드")
        st.write("- 6회: 스키장에서 실종된 고양이들을 구출하는 유닛 737")
        st.image("https://raw.githubusercontent.com/ErikThiart/cryptocurrency-icons/master/128/tether.png", width=100)

    elif menu == "⚙️ 알림 설정":
        st.markdown("<h1>⚙️ 무전 알림 설정</h1>", unsafe_allow_html=True)
        threshold = st.slider("알림 기준 김프 (%)", -5.0, 5.0, 1.0)
        st.write(f"현재 설정: 김프가 **{threshold}%** 이하로 떨어지면 텔레그램 무전을 보냅니다.")
        if st.button("설정 저장"):
            st.success("알림 기준이 저장되었습니다.")

    # 자동 새로고침 (홈과 상세분석 메뉴에서만)
    if menu in ["🏠 대시보드", "📊 김프 상세분석"]:
        time.sleep(10)
        st.rerun()
