import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 모바일 최적화 및 잔상 방지 스타일 ---
def apply_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        
        /* 제목 디자인: 줄바꿈 방지 및 중앙 정렬 */
        .main-title { 
            text-align: center; color: #26A17B; font-weight: 700; 
            font-size: 22px; white-space: nowrap; margin-bottom: 25px;
        }
        
        /* 로그인 카드 스타일 (녹색 바탕) */
        .login-card { background-color: #26A17B; padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; }
        
        /* 지표 카드 (한화 표시 강조) */
        .metric-card { 
            background-color: white; padding: 15px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #26A17B;
            margin-bottom: 10px; text-align: center;
        }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 통합 수집 및 한화 변환 ---
def get_all_market_data():
    try:
        # 1. 업비트 (KRW)
        up = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
        
        # 2. 실시간 환율
        ex_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        ex_rate = float(ex_res['rates']['KRW'])
        
        # 3. 바이낸스 (USD -> KRW 변환)
        bn_usd = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        bn_krw = bn_usd * ex_rate
        
        # 4. OKX (USD -> KRW 변환)
        ok_res = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()
        ok_usd = float(ok_res['data'][0]['last'])
        ok_krw = ok_usd * ex_rate
        
        # 김프 계산 (해외 평균 대비)
        avg_global_krw = (bn_krw + ok_krw) / 2
        kimp = ((float(up) / avg_global_krw) - 1) * 100
        
        return float(up), bn_krw, ok_krw, ex_rate, kimp
    except:
        return None, None, None, None, None

# --- 3. 시스템 설정 ---
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'chart_data' not in st.session_state: st.session_state['chart_data'] = []

apply_premium_style()

# --- [화면 1: 깨끗한 로그인] ---
if not st.session_state['authenticated']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<div class='login-card'><h2>AI 오두막 터미널</h2><p>Ar & Or & Unit 737</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠(Password)", type="password")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['authenticated'] = True
                st.rerun() # 로그인 성공 시 화면 전체 청소 후 이동
            else: st.error("열쇠가 맞지 않습니다.")

# --- [화면 2: 번듯한 대시보드] ---
else:
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    up, bn_k, ok_k, ex, k = get_all_market_data()
    
    if up:
        # 상단 3열: 거래소별 가격 (모두 한화 KRW 기준)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
        with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원")
        with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원")
        
        # 중앙: 실시간 김프 및 환율 정보
        st.write("---")
        color = "normal" if k > 0 else "inverse"
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            st.metric("📊 실시간 김프", f"{k:.2f}%", delta=f"{k:.2f}%", delta_color=color)
        with col_sub2:
            st.metric("💵 기준 환율", f"{ex:,.1f}원")
            
        # 하단: 그래프
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_data'].append({"시간": now, "김프": k})
        if len(st.session_state['chart_data']) > 30: st.session_state['chart_data'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['chart_data'])
        st.line_chart(df.set_index("시간"))
        
        st.caption(f"최근 갱신: {now} (10초 자동 갱신)")
        
        # 사이드바 (로그아웃)
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("안전 로그아웃"):
                st.session_state['authenticated'] = False
                st.rerun()
        
        time.sleep(10); st.rerun()
    else:
        st.info("🔄 유닛 737이 전 세계 거래소를 돌며 데이터를 낚는 중입니다...")
        time.sleep(3); st.rerun()
