import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 🌟 [필수] 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 전문가용 프리미엄 스타일 (다크 모드 최적화)
def apply_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #0e1117; }
        
        .main-title { text-align: center; color: #26A17B; font-weight: 700; font-size: 24px; margin-bottom: 25px; }
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
        
        /* 지표 카드 디자인 */
        [data-testid="stMetric"] {
            background-color: #1e2129;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
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
if 'chart_history' not in st.session_state: st.session_state['chart_history'] = []

apply_style()

# ---------------------------------------------------------
# 🛡️ [아빠님 솔루션] 메인 플레이스홀더 생성 및 입구 검문
# ---------------------------------------------------------
main_placeholder = st.empty()

with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.1, 0.8, 0.1])
        with col_login:
            st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Terminal</p></div>", unsafe_allow_html=True)
            # key를 추가하여 위젯 재사용 방지
            pw = st.text_input("오두막 열쇠 (PW)", type="password", key="pw_input")
            if st.button("시스템 접속", key="login_btn"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    # [핵심] 즉시 비우고 타이밍 보정 후 rerun
                    main_placeholder.empty()
                    time.sleep(0.15)
                    st.rerun()
                else:
                    st.error("열쇠가 맞지 않습니다.")
        # 안전장치 유지
        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 여기서부터는 로그인 성공 시에만 렌더링됨
# ---------------------------------------------------------

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 데이터 수집 (업비트, 바이낸스, OKX, 환율)
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    # 💰 모든 가격을 '한화(KRW)'로 자동 변환
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    # 상단 3열 비교
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    # 중앙 김프 및 환율
    st.write("---")
    avg_global = [p for p in [bn_k, ok_k] if p]
    if avg_global:
        k_val = ((up_k / (sum(avg_global)/len(avg_global))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        col_res1, col_res2 = st.columns(2)
        with col_res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with col_res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 📈 실시간 변화 그래프
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['chart_history']) > 30: st.session_state['chart_history'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['chart_history'])
        st.line_chart(df.set_index("시간"))
    
    st.caption(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')} (12초 자동 갱신 중)")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("안전 로그아웃"):
            st.session_state['auth'] = False
            st.rerun()
            
    # 아빠님 조언대로 부하를 줄이기 위해 12초로 살짝 조정
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 유닛 737이 전 세계 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
