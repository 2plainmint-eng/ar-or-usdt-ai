import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 모바일 최적화 프리미엄 스타일 ---
def apply_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        
        /* 제목: 모바일에서 줄바꿈 방지 (글자 크기 자동 조절) */
        .main-title { 
            text-align: center; 
            color: #26A17B; 
            font-weight: 700; 
            font-size: calc(1.5rem + 1vw); /* 화면 폭에 따라 조절 */
            white-space: nowrap; 
            margin-bottom: 20px;
            letter-spacing: -1px;
        }
        
        /* 로그인 카드 (아빠님 마음에 드신 그 스타일) */
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        
        /* 지표 카드: 깔끔하게 박스 처리 */
        .metric-box { 
            background-color: white; 
            padding: 15px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
            border-top: 4px solid #26A17B;
            text-align: center;
            margin-bottom: 10px;
        }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 이중 우회로 장착 (로딩 멈춤 방지) ---
def fetch_all_data():
    try:
        # 업비트
        up = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
        
        # 바이낸스 (안되면 다른 경로로 즉시 우회)
        try:
            bn = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        except:
            bn = float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()['data'][0]['last'])
            
        # 환율 (안되면 글로벌 우회)
        try:
            ex = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
        except:
            ex = float(requests.get("https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD", headers={'User-Agent':'Mozilla/5.0'}).json()[0]['basePrice'])
        
        kimp = ((float(up) / (bn * ex)) - 1) * 100
        return float(up), bn, ex, kimp
    except:
        return None, None, None, None

# --- 3. 시스템 엔진 ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'history' not in st.session_state: st.session_state['history'] = []

apply_style()

# --- [페이지 1: 로그인] ---
if not st.session_state['auth']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.05, 0.9, 0.05])
    with c2:
        st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737</p></div>", unsafe_allow_html=True)
        u_id = st.text_input("아이디", value="admin")
        u_pw = st.text_input("비밀번호", type="password")
        if st.button("시스템 접속"):
            if u_pw == "aror737":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("정보를 확인해 주세요.")

# --- [페이지 2: 대시보드] ---
else:
    # ⚓ 제목 중앙 정렬 및 폰트 고정
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    # 데이터 가져오기
    up, bn, ex, k = fetch_all_data()
    
    if up:
        # 1. 상단 비교 지표 (3열)
        col_m = st.columns(3)
        with col_m[0]: st.metric("🔶 바이낸스", f"{bn:.4f}$")
        with col_m[1]: st.metric("💵 환율(기준)", f"{ex:,.0f}원")
        with col_m[2]: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        
        # 2. 중앙 김프 지표 (강조)
        st.write("---")
        color = "normal" if k > 0 else "inverse"
        st.metric("📊 실시간 김치 프리미엄", f"{k:.2f}%", delta=f"{k:.2f}%", delta_color=color)
        
        # 3. 하단 실시간 변화 그래프
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['history'].append({"시간": now, "김프": k})
        if len(st.session_state['history']) > 20: st.session_state['history'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['history'])
        st.line_chart(df.set_index("시간"))
        
        st.caption(f"업데이트: {now} (10초 자동 갱신)")
        
        # 사이드바 메뉴
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("안전 로그아웃"):
                st.session_state['auth'] = False
                st.rerun()
        
        time.sleep(10); st.rerun()
    else:
        st.warning("🔄 유닛 737이 긴급 우회 경로로 데이터를 낚는 중입니다...")
        time.sleep(3); st.rerun()
