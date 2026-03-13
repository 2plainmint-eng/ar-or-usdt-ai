import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide")

# 2. 🎨 [디자인] 초고대비 프리미엄 스타일 (서브헤더 보강)
def apply_ultra_contrast_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 전체 배경 */
        .stApp { background-color: #0e1117 !important; }
        
        /* [수정] 메인 제목 & 서브 제목 (최근 변화 추이 등) 강제 흰색 */
        .main-title, h1, h2, h3, .stSubheader { 
            text-align: center; 
            color: #ffffff !important; 
            font-weight: 700 !important; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        
        .main-title { 
            color: #26A17B !important; 
            font-size: clamp(1.5rem, 6vw, 2.2rem); 
            margin: 20px 0; 
        }

        /* [수정] 최근 변화 추이 글자 시인성 강화 */
        .stMarkdown h3 {
            color: #ffffff !important;
            font-size: clamp(1.2rem, 5vw, 1.6rem) !important;
            margin-top: 30px !important;
            border-left: 5px solid #26A17B;
            padding-left: 10px;
            text-align: left !important; /* 모바일 가독성을 위해 왼쪽 정렬 */
        }
        
        /* 지표 카드 스타일 */
        [data-testid="stMetric"] {
            background-color: #1e2129 !important;
            padding: 20px !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
            border: 1px solid #333 !important;
            border-top: 5px solid #26A17B !important;
        }
        
        /* 지표 숫자 쨍하게 고정 */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-size: clamp(1.8rem, 7vw, 2.8rem) !important;
            font-weight: 800 !important;
        }
        
        /* 지표 라벨 (업비트, 바이낸스 등) */
        [data-testid="stMetricLabel"] p {
            color: #d1d1d1 !important;
            font-size: clamp(0.9rem, 4vw, 1.1rem) !important;
        }

        /* 버튼 디자인 */
        div.stButton > button { 
            background-color: #26A17B; color: white; border-radius: 12px; 
            font-weight: 700; width: 100%; height: 4em; border: none;
        }
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

apply_ultra_contrast_style()

# ---------------------------------------------------------
# 🛡️ [아빠님 솔루션] 잔상 방지 100% 적용
# ---------------------------------------------------------
main_placeholder = st.empty()

with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_login, _ = st.columns([0.05, 0.9, 0.05])
        with col_login:
            st.markdown("<div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access</p></div>", unsafe_allow_html=True)
            pw = st.text_input("오두막 열쇠 (PW)", type="password", key="pw_final")
            if st.button("시스템 접속", key="btn_final"):
                if pw == "aror737":
                    st.session_state['auth'] = True
                    main_placeholder.empty()
                    time.sleep(0.15) # 아빠님의 타이밍 보정 묘수
                    st.rerun()
                else:
                    st.error("열쇠가 맞지 않습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 [대시보드] 옥에 티 박멸 렌더링
# ---------------------------------------------------------

st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)

# 데이터 수집
up_k = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

if up_k and ex:
    bn_k = (bn_u * ex) if bn_u else None
    ok_k = (ok_u * ex) if ok_u else None
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🇰🇷 업비트", f"{up_k:,.0f}원")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
    
    st.write("---")
    
    avg_global = [p for p in [bn_k, ok_k] if p]
    if avg_global:
        k_val = ((up_k / (sum(avg_global)/len(avg_global))) - 1) * 100
        color = "normal" if k_val > 0 else "inverse"
        
        res1, res2 = st.columns(2)
        with res1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
        with res2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
        
        # 차트 기록
        now = datetime.now().strftime('%H:%M:%S')
        st.session_state['chart_history'].append({"시간": now, "김프": k_val})
        if len(st.session_state['chart_history']) > 25: st.session_state['chart_history'].pop(0)
        
        st.write("---")
        # 💡 흐릿했던 부분을 명확하게 수정
        st.subheader("📉 최근 변화 추이")
        df = pd.DataFrame(st.session_state['chart_history'])
        st.line_chart(df.set_index("시간"))
    
    st.caption(f"최근 갱신: {now} (12초 자동 갱신 중)")
    
    with st.sidebar:
        st.success("⚓ 아르 아빠님 접속 중")
        if st.button("안전 로그아웃"):
            st.session_state['auth'] = False
            st.rerun()
            
    time.sleep(12)
    st.rerun()
else:
    st.info("🎣 유닛 737이 전 세계 데이터를 낚는 중입니다...")
    time.sleep(3)
    st.rerun()
