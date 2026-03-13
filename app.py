import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 전문가용 프리미엄 스타일 설정 ---
def apply_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        
        /* 제목 디자인 */
        .main-title { 
            text-align: center; color: #26A17B; font-weight: 700; 
            font-size: 24px; white-space: nowrap; margin-bottom: 25px;
        }
        
        /* 로그인 카드 (녹색 바탕) */
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
        
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

# --- 2. [데이터] 개별 낚시 엔진 (모든 가격 KRW 변환) ---
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys:
            res = res[k]
        return float(res)
    except:
        return None

# --- 3. 시스템 초기 세팅 ---
if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
if 'chart_history' not in st.session_state: st.session_state['chart_history'] = []

apply_premium_style()

# --- [비즈니스 로직: 잔상 박멸 분기점] ---

# 1. 로그인이 아직 안 된 경우 -> 로그인 창만 보여줌
if not st.session_state['is_logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<div class='login-card'><h2>AI 오두막 터미널</h2><p>Ar & Or & Unit 737 Login</p></div>", unsafe_allow_html=True)
        password_input = st.text_input("오두막 열쇠 (PW)", type="password")
        if st.button("시스템 접속"):
            if password_input == "aror737":
                st.session_state['is_logged_in'] = True
                st.rerun() # 성공 즉시 화면을 싹 비우고 다시 시작!
            else:
                st.error("열쇠가 맞지 않습니다.")

# 2. 로그인 성공 시 -> 대시보드만 보여줌 (잔상이 남을 수 없는 구조)
else:
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    # 데이터 수집 (업비트, 바이낸스, OKX, 환율)
    up_krw = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
    ex_rate = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
    bn_usd = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
    ok_usd = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])
    
    # 데이터가 하나라도 있으면 화면 구성
    if up_krw and ex_rate:
        # 해외 거래소 달러 -> 한화(KRW) 자동 변환
        bn_krw = (bn_usd * ex_rate) if bn_usd else None
        ok_krw = (ok_usd * ex_rate) if ok_usd else None
        
        # 상단 3열 비교 지표 (모두 한화로 통일!)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("🇰🇷 업비트", f"{up_krw:,.0f}원")
        with col2: st.metric("🔶 바이낸스", f"{bn_krw:,.0f}원" if bn_krw else "대기중")
        with col3: st.metric("🖤 OKX", f"{ok_krw:,.0f}원" if ok_krw else "대기중")
        
        # 중앙 김프 계산 (해외 거래소 평균가 기준)
        st.write("---")
        avg_global = [p for p in [bn_krw, ok_krw] if p]
        
        if avg_global:
            k_val = ((up_krw / (sum(avg_global)/len(avg_global))) - 1) * 100
            color = "normal" if k_val > 0 else "inverse"
            
            c_k1, c_k2 = st.columns(2)
            with c_k1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
            with c_k2: st.metric("💵 기준 환율", f"{ex_rate:,.1f}원")
            
            # 그래프 기록
            now = datetime.now().strftime('%H:%M:%S')
            st.session_state['chart_history'].append({"시간": now, "김프": k_val})
            if len(st.session_state['chart_history']) > 30: st.session_state['chart_history'].pop(0)
            
            st.write("---")
            st.subheader("📉 김프 실시간 변화 차트")
            df = pd.DataFrame(st.session_state['chart_history'])
            st.line_chart(df.set_index("시간"))
            
        st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신 중)")
        
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("안전 로그아웃"):
                st.session_state['is_logged_in'] = False
                st.rerun()
                
        time.sleep(10); st.rerun()
    else:
        st.info("🎣 유닛 737이 전 세계 거래소 데이터를 낚는 중입니다... (약 5초 소요)")
        time.sleep(3); st.rerun()
