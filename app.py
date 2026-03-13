import streamlit as st
import ccxt
import requests
import time
import pandas as pd
import datetime

# 1. 🌟 페이지 설정
st.set_page_config(
    page_title="테더 USDT 전용 김프 자동화 매매 AI",
    page_icon="🟢",
    layout="wide"
)

# 2. 🗄️ 회원 시스템
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {"admin": "aror737"}
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# --- 사이드바 (에메랄드 제어판) ---
with st.sidebar:
    # 🌟 녹색 테더 로고를 인터넷 주소로 직접 불러옵니다 (에러 원천 차단!)
    st.markdown(f"""
        <div style='text-align: center;'>
            <img src="https://cryptologos.cc/logos/tether-usdt-logo.png" width="180">
            <h1 style='color: #26A17B; margin-top: 15px;'>USDT AI TRADER</h1>
            <p style='color: #888888; font-size: 16px;'>테더 전용 자동화 매매 시스템</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    if st.session_state['logged_in_user'] is None:
        st.subheader("🔐 시스템 접속")
        menu = st.radio("작업 선택", ["로그인", "회원가입"])
        
        if menu == "회원가입":
            new_user = st.text_input("사용자 등록", placeholder="성함을 입력하세요")
            new_pw = st.text_input("비밀번호 설정", type="password")
            if st.button("신규 회원 등록"):
                if new_user in st.session_state['user_db']:
                    st.warning("이미 등록된 사용자입니다.")
                else:
                    st.session_state['user_db'][new_user] = new_pw
                    st.success(f"{new_user}님, 등록 완료!")
        else:
            user_id = st.text_input("아이디")
            user_pw = st.text_input("비밀번호", type="password")
            if st.button("AI 시스템 접속"):
                if user_id in st.session_state['user_db'] and st.session_state['user_db'][user_id] == user_pw:
                    st.session_state['logged_in_user'] = user_id
                    st.rerun()
                else:
                    st.error("정보가 일치하지 않습니다.")
        st.stop()
    else:
        st.success(f"🟢 {st.session_state['logged_in_user']}님, 가동 중")
        if st.button("안전 로그아웃"):
            st.session_state['logged_in_user'] = None
            st.rerun()
        st.write("---")
        my_money = st.slider("💰 가상 투자금 (만원)", 10, 5000, 1000)
        target_kimp = st.number_input("🎯 목표 김프 (%)", value=1.0, step=0.1)

# --- 메인 화면 ---

def get_data():
    u_price, rate = 0, 1410.0
    try:
        upbit = ccxt.upbit()
        u_price = upbit.fetch_ticker('USDT/KRW')['last']
        res = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=2)
        rate = res.json()['rates']['KRW']
    except: pass
    return u_price, rate

u_price, rate = get_data()

if 'history' not in st.session_state:
    st.session_state['history'] = pd.DataFrame(columns=['시간', '김프'])

if u_price > 0:
    premium = ((u_price / rate) - 1) * 100
    now = datetime.datetime.now().strftime('%H:%M:%S')
    new_data = pd.DataFrame({'시간': [now], '김프': [premium]})
    st.session_state['history'] = pd.concat([st.session_state['history'], new_data]).tail(20)

    # 제목을 전문적인 녹색으로!
    st.markdown(f"<h1 style='text-align: center; color: #26A17B;'>📈 테더 USDT 전용 김프 자동화 매매 AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888888;'>분석가: {st.session_state['logged_in_user']}님 전용 터미널</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    # 지표 카드
    c1, c2, c3 = st.columns(3)
    c1.metric("🇰🇷 업비트 (USDT)", f"{u_price:,.1f}원")
    c2.metric("🇺🇸 기준 환율", f"{rate:,.1f}원")
    c3.metric("💎 실시간 김프", f"{premium:.2f}%", delta=f"{premium:.2f}%")

    st.write("---")

    # 분석 섹션
    st.subheader("🤖 AI 매매 전략 분석")
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.line_chart(st.session_state['history'].set_index('시간'), color="#26A17B")
    
    with col_r:
        profit = (my_money * 10000) * (premium / 100)
        st.write(f"투자금: **{my_money:,}만원**")
        st.write("예상 프리미엄 가치:")
        st.markdown(f"<h1 style='color: #26A17B;'>{profit:,.0f}원</h1>", unsafe_allow_html=True)
        
        if premium <= target_kimp:
            st.error("🎯 [매수 권장] 김프 낮음")
            st.balloons()
        else:
            st.success("⌛ [관망] 김프 대기 중")

else:
    st.warning("📡 데이터 서버에 접속 중입니다...")

time.sleep(3)
st.rerun()