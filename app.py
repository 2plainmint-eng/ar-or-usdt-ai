import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 🌟 [필수] 페이지 설정 및 반응형 메타태그
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 모바일 최적화 프리미엄 스타일
def apply_mobile_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 전체 배경 및 폰트 */
        html, body, [class*="css"] { 
            font-family: 'Noto+Sans+KR', sans-serif; 
            background-color: #0e1117; 
            color: #ffffff;
        }
        
        /* 제목: 모바일 가독성 핵심 (화면 폭에 따라 자동 조절) */
        .main-title { 
            text-align: center; 
            color: #26A17B; 
            font-weight: 700; 
            font-size: clamp(1.2rem, 5vw, 2rem); 
            white-space: nowrap;
            margin: 20px 0;
            letter-spacing: -1px;
        }
        
        /* 로그인 카드 (모바일 터치 최적화) */
        .login-card { 
            background-color: #26A17B; 
            padding: 30px 20px; 
            border-radius: 20px; 
            color: white; 
            text-align: center; 
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }
        
        /* 지표 카드 (모바일에서 더 큼직하게) */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important;
            padding: 20px !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
            border-top: 5px solid #26A17B !important;
        }
        
        /* 모바일에서 글자 크기 강제 확대 */
        [data-testid="stMetricValue"] {
            font-size: clamp(1.5rem, 6vw, 2.5rem) !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: clamp(0.9rem, 4vw, 1.1rem) !important;
            color: #aaaaaa !important;
        }

        /* 버튼 크기 키우기 */
        div.stButton > button { 
            background-color: #26A17B; 
            color: white; 
            border-radius: 12px; 
            font-weight: 700; 
            width: 100%; 
            height: 4em; 
            border: none;
            font-size: 1.1rem;
        }
        
        /* 모바일 구분선 여백 조절 */
        hr { margin: 1.5rem 0 !important; opacity: 0.2; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# 초기 세션 설정
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'chart_history' not in st.session_state: st.session_state['chart_history'] = []

apply_mobile_style()

# ---------------------------------------------------------
# 🛡️ [아빠님의 잔상 방지 솔루션] 컨테이너 및 검문
# ---------------------------------------------------------
main_placeholder = st.empty()

with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.05, 0.9, 0.05])
        with col_login:
            st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access</p></div>", unsafe_allow_html=True)
            pw = st.text_input("오두막 열쇠 (PW)", type="password", key="pw_mobile")
            if st.button("시스템 접속", key="btn_mobile"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    main_placeholder.empty()
                    time.sleep(0.15) # 아빠님의 타이밍 보정 묘수!
                    st.rerun()
                else:
                    st.error("열쇠가 맞지 않습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 모바일 최적화 렌더링
# ---------------------------------------------------------

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 데이터 수집 (업비트, 바이낸스, OKX, 환율)
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    # 💰 모든 해외 가격을 '한화(KRW)'로 자동 변환
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    # 상단 3열 비교 (모바일에서는 자동으로 아래로 쌓임)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    st.write("---")
    
    # 중앙 김프 및 환율
    avg_global = [p for p in [bn_k, ok_k] if p]
    if avg_global:
        k_val = ((up_k / (sum(avg_global)/len(avg_global))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        res1, res2 = st.columns(2)
        with res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 📈 차트 기록
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['chart_history']) > 20: st.session_state['chart_history'].pop(0)
        
        st.write("---")
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['chart_history'])
        st.line_chart(df.set_index("시간"))
    
    st.caption(f"최근 갱신: {now} (12초 자동 갱신 중)")
    
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>⚓ NAVIGATION</h2>", unsafe_allow_html=True)
        if st.button("안전 로그아웃", key="logout_mobile"):
            st.session_state['auth'] = False
            st.rerun()
            
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 유닛 737이 전 세계 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
