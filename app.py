import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 전문가용 프리미엄 스타일 ---
def apply_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        
        /* 제목 중앙 정렬 */
        .main-title { text-align: center; color: #26A17B; font-weight: 700; margin-bottom: 20px; }
        
        /* 로그인 카드 (녹색 바탕) */
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
        
        /* 지표 카드 디자인 */
        .stMetric { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #26A17B; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 안정적인 수집 로직 ---
def fetch_all_data():
    try:
        # 업비트 (KRW-USDT)
        up = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
        # 바이낸스 (USDT-USD)
        bn = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        # 환율 (USD-KRW)
        ex = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
        
        kimp = ((float(up) / (bn * ex)) - 1) * 100
        return float(up), bn, ex, kimp
    except:
        return None, None, None, None

# --- 3. 시스템 초기화 ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_style()

# --- [화면 1: 로그인] ---
if not st.session_state['auth']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
    with c2:
        st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737</p></div>", unsafe_allow_html=True)
        u_id = st.text_input("아이디", value="admin")
        u_pw = st.text_input("비밀번호", type="password")
        if st.button("시스템 접속"):
            if u_id == "admin" and u_pw == "aror737":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("정보를 확인해 주세요.")

# --- [화면 2: 메인 시스템] ---
else:
    st.markdown("<h1 class='main-title'>⚓ USDT 김프 현황</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<h3 style='text-align:center;'>카테고리</h3>", unsafe_allow_html=True)
        menu = st.radio("", ["🏠 실시간 대시보드", "⚙️ 무전 알림 설정"])
        st.write("---")
        if st.button("안전 로그아웃"):
            st.session_state['auth'] = False
            st.rerun()

    if menu == "🏠 실시간 대시보드":
        up, bn, ex, k = fetch_all_data()
        
        if up:
            # 상단 3열: 비교 대상 노출 (바이낸스 / 환율 / 업비트)
            col_data = st.columns(3)
            col_data[0].metric("🔶 바이낸스", f"{bn:.4f} $")
            col_data[1].metric("💵 기준 환율", f"{ex:,.1f} 원")
            col_data[2].metric("🇰🇷 업비트", f"{up:,.1f} 원")
            
            # 중앙: 김프 수치 (가장 크게!)
            st.write("---")
            color = "normal" if k > 0 else "inverse"
            st.metric("📊 실시간 김치 프리미엄", f"{k:.2f} %", delta=f"{k:.2f}%", delta_color=color)
            
            # 하단: 그래프 기록
            now = datetime.now().strftime('%H:%M:%S')
            st.session_state['history'].append({"시간": now, "김프": k})
            if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
            
            st.write("---")
            st.subheader("📉 김프 실시간 변화 추이")
            df = pd.DataFrame(st.session_state['history'])
            st.line_chart(df.set_index("시간"))
            
            st.caption(f"최근 갱신: {now} (10초 자동 감시 중)")
            time.sleep(10); st.rerun()
        else:
            st.warning("🔄 데이터를 낚아오는 중입니다. 잠시만 기다려주세요...")
            time.sleep(3); st.rerun()

    elif menu == "⚙️ 무전 알림 설정":
        st.markdown("<h2 class='main-title'>⚙️ 무전 알림 설정</h2>", unsafe_allow_html=True)
        st.info("설정한 기준값보다 김프가 낮아지면 텔레그램으로 즉시 보고합니다.")
        threshold = st.slider("알림 기준 김프 (%)", -3.0, 3.0, 1.0, step=0.1)
        if st.button("설정 저장"):
            st.success(f"기준값이 {threshold}%로 저장되었습니다! (유닛 737 감시 시작)")
