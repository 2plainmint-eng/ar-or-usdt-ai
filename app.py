import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. [디자인] 전문가용 프리미엄 스타일 ---
def apply_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        
        .main-title { text-align: center; color: #26A17B; font-weight: 700; font-size: 22px; margin-bottom: 25px; }
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; }
        .metric-card { 
            background-color: white; padding: 15px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #26A17B;
            text-align: center; margin-bottom: 10px;
        }
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 개별 낚시 엔진 (한화 자동 변환) ---
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# --- 3. [중요] 시스템 설정 및 페이지 구성 ---
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")
apply_premium_style()

if 'is_auth' not in st.session_state: st.session_state['is_auth'] = False
if 'chart_logs' not in st.session_state: st.session_state['chart_logs'] = []

# --- [철통 검문] 로그인 로직을 맨 위로 배치 ---
if not st.session_state['is_auth']:
    # 로그인이 안 된 상태에서는 오직 이 화면만 보여주고 멈춤!
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([0.1, 0.8, 0.1])
    with col_login:
        st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Terminal</p></div>", unsafe_allow_html=True)
        pw_input = st.text_input("오두막 열쇠 (PW)", type="password")
        if st.button("시스템 접속"):
            if pw_input == "aror737":
                st.session_state['is_auth'] = True
                st.rerun() # 성공 시 화면을 싹 지우고 다시 처음부터 읽음
            else:
                st.error("열쇠가 맞지 않습니다.")
    # 아래의 대시보드 코드로 넘어가지 못하게 강제 중단
    st.stop()

# --- [대시보드] 로그인 성공 시에만 여기서부터 읽음 ---

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 🎣 데이터 수집
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    # 💰 모든 가격을 한화(KRW)로 자동 변환 (아빠님 요청사항)
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    # 상단 3열: 한화 비교 지표
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    # 중앙: 김프 및 환율
    st.write("---")
    avg_global = [p for p in [bn_k, ok_k] if p]
    if avg_global:
        k_val = ((up_k / (sum(avg_global)/len(avg_global))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        col_res1, col_res2 = st.columns(2)
        with col_res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with col_res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 📈 그래프 업데이트
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_logs'].append({"시간": now, "김프": k_val})
        if len(st.session_state['chart_logs']) > 30: st.session_state['chart_logs'].pop(0)
        
        st.write("---")
        st.subheader("📉 김프 실시간 변화 차트")
        df = pd.DataFrame(st.session_state['chart_logs'])
        st.line_chart(df.set_index("시간"))
    
    st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신 중)")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("안전 로그아웃"):
            st.session_state['is_auth'] = False
            st.rerun()
            
    time.sleep(10); st.rerun()
else:
    st.info("🎣 유닛 737이 전 세계 거래소 데이터를 낚는 중입니다... (약 5초 소요)")
    time.sleep(3); st.rerun()
