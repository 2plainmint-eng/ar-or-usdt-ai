import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 🌟 [필수] 페이지 설정 (무조건 맨 위!)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 전문가용 프리미엄 스타일
def apply_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; }
        
        /* 제목 디자인 */
        .main-title { text-align: center; color: #26A17B; font-weight: 700; font-size: 24px; margin-bottom: 25px; }
        
        /* 로그인 카드 (녹색 바탕) */
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
        
        /* 지표 카드 (시인성 강화) */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            border-top: 5px solid #26A17B;
        }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 낚시 엔진
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# 초기 상태 설정
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'chart_logs' not in st.session_state: st.session_state['chart_logs'] = []

apply_style()

# ---------------------------------------------------------
# 🛡️ [중요] 현관문 검문소 (로그인 전에는 아래 코드를 아예 안 읽음)
# ---------------------------------------------------------
if not st.session_state['auth']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([0.1, 0.8, 0.1])
    with col_login:
        st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access</p></div>", unsafe_allow_html=True)
        pw = st.text_input("오두막 열쇠 (PW)", type="password")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                st.rerun() # 성공 즉시 화면을 싹 지우고 다시 시작
            else:
                st.error("열쇠가 맞지 않습니다.")
    
    # 🚨 여기가 핵심! 로그인이 안 됐으면 여기서 코드를 '강제 종료' 합니다.
    # 이 아래에 있는 대시보드 코드는 컴퓨터가 쳐다보지도 못하게 합니다.
    st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 로그인 성공 시에만 여기서부터 실행됨
# ---------------------------------------------------------

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 데이터 수집 (업비트, 바이낸스, OKX, 환율)
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    # 💰 모든 해외 가격을 '한화(KRW)'로 즉시 변환 (아빠님 요청)
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    # 상단 3열 비교 (전부 원화 단위)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    # 중앙 김프 및 환율
    st.write("---")
    avg_global = [p for p in [bn_k, ok_k] if p]
    if avg_global:
        current_kimp = ((up_k / (sum(avg_global)/len(avg_global))) - 1) * 100
        color = "normal" if current_kimp > 0 else "inverse"
        
        col_res1, col_res2 = st.columns(2)
        with col_res1: st.metric("📊 실시간 김프", f"{current_kimp:.2f}%", delta=f"{current_kimp:.2f}%", delta_color=color)
        with col_res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 📈 실시간 변화 그래프
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_logs'].append({"시간": now, "김프": current_kimp})
        if len(st.session_state['chart_logs']) > 30: st.session_state['chart_logs'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['chart_logs'])
        st.line_chart(df.set_index("시간"))
    
    st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (10초 자동 감시 중)")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("안전 로그아웃"):
            st.session_state['auth'] = False
            st.rerun()
            
    time.sleep(10); st.rerun()
else:
    st.info("🎣 유닛 737이 바다 깊은 곳에서 데이터를 낚는 중입니다... (약 5초 소요)")
    time.sleep(3); st.rerun()
