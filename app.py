import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 4열 레이아웃 스타일
def apply_transparent_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important; font-size: clamp(1.5rem, 6vw, 2.5rem) !important;
            font-weight: 900 !important; text-shadow: 1px 1px 2px rgba(0,0,0,1);
        }
        
        /* 지표 라벨 (거래소 이름) */
        [data-testid="stMetricLabel"] p {
            color: #26A17B !important; font-size: clamp(0.8rem, 3vw, 1rem) !important; font-weight: 700 !important;
        }

        .main-title { text-align: center; color: #26A17B; font-weight: 900; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 20px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 5px solid #26A17B !important; padding: 15px !important; border-radius: 12px !important; }
        
        /* 비교 기준가 강조 */
        .base-info { background-color: #26A17B; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: 700; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 엔진
def get_safe_price(exchange):
    try:
        # 타임아웃을 5초로 늘려 대기 현상을 줄임
        if exchange == "up": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
        if exchange == "bn": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()['price'])
        if exchange == "ok": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()['data'][0]['last'])
        if exchange == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['KRW'])
    except: return None

# 세션 초기화
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'menu' not in st.session_state: st.session_state['menu'] = "kimp"
if 'history' not in st.session_state: st.session_state['history'] = []

apply_transparent_style()

# 🛡️ 로그인 검문소
main_placeholder = st.empty()
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="pw_v28")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty(); time.sleep(0.15); st.rerun()
            else: st.error("틀렸습니다.")
        st.stop()

# 📈 메인 대시보드
st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 상단 메뉴
col_m1, col_m2 = st.columns(2)
with col_m1: 
    if st.button("📊 실시간 김프", use_container_width=True): st.session_state['menu'] = "kimp"
with col_m2: 
    if st.button("💹 가상 매매", use_container_width=True): st.session_state['menu'] = "trade"

# 데이터 수집
up = get_safe_price("up"); bn = get_safe_price("bn"); ok = get_safe_price("ok"); ex = get_safe_price("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None

# 💡 김프 계산의 투명성 확보
avg_list = []
sources = []
if bn_k: 
    avg_list.append(bn_k); sources.append("바이낸스")
if ok_k: 
    avg_list.append(ok_k); sources.append("OKX")

global_avg = sum(avg_list)/len(avg_list) if avg_list else 0
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0

if st.session_state['menu'] == "kimp":
    # 💡 누구랑 비교 중인지 알려주는 배너
    if sources:
        st.markdown(f"<div class='base-info'>📢 현재 비교 대상: {' + '.join(sources)} (평균 {global_avg:,.0f}원)</div>", unsafe_allow_html=True)
    else:
        st.error("해외 거래소 연결 대기 중입니다.")

    # 4열 배치로 모든 비교군 노출
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원" if up else "대기")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
    with c4: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).strftime('%H:%M:%S')
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    st.caption(f"기준 환율: {ex:,.1f}원 | 갱신: {now}")
    
    time.sleep(15); st.rerun()

else:
    st.info("💹 가상 매매 모드입니다. 상단 버튼으로 전환하세요.")
