import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 페이지 설정 (반드시 맨 위에 있어야 함)
st.set_page_config(page_title="아르아빠의 즐거운 AI 생활", layout="wide")

# 2. [디자인] 전문가용 프리미엄 스타일
def apply_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+KR', sans-serif; background-color: #f8f9fa; }
        .main-title { text-align: center; color: #26A17B; font-weight: 700; font-size: 24px; margin-bottom: 25px; }
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; }
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        /* 잔상 방지를 위한 메트릭 숨김 처리 */
        [data-testid="stMetric"] { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #26A17B; }
        </style>
    """, unsafe_allow_html=True)

# 3. 데이터 낚시 엔진
def get_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys: res = res[k]
        return float(res)
    except: return None

# 초기 상태 설정
if 'is_auth' not in st.session_state: st.session_state['is_auth'] = False
if 'logs' not in st.session_state: st.session_state['logs'] = []

apply_style()

# ---------------------------------------------------------
# [중요] 화면 전체를 담는 컨테이너 생성 (유령 박멸의 핵심)
# ---------------------------------------------------------
placeholder = st.empty()

with placeholder.container():
    # 1. 로그인이 안 된 상태
    if not st.session_state['is_auth']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([0.1, 0.8, 0.1])
        with col:
            st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Access Only</p></div>", unsafe_allow_html=True)
            pw = st.text_input("오두막 열쇠 (PW)", type="password")
            if st.button("시스템 접속"):
                if pw == "aror737":
                    st.session_state['is_auth'] = True
                    st.rerun() # 성공 즉시 화면 싹 비우기
                else:
                    st.error("열쇠가 맞지 않습니다.")
        st.stop() # <-- 로그인 안 됐으면 아래 코드는 아예 읽지도 않음

    # 2. 로그인 성공 시 (여기서부터만 대시보드를 그립니다)
    else:
        st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
        
        # 데이터는 여기서 '비밀스럽게' 수집 시작
        up = get_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
        ex = get_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
        bn_u = get_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
        ok_u = get_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

        if up and ex:
            # 모든 가격을 한화(KRW)로 변환
            bn_k = (bn_u * ex) if bn_u else None
            ok_k = (ok_u * ex) if ok_u else None
            
            # 상단 지표 (깔끔한 3열)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원")
            with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기중")
            with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기중")
            
            # 김프 계산
            st.write("---")
            avg_g = [p for p in [bn_k, ok_k] if p]
            if avg_g:
                k_val = ((up / (sum(avg_g)/len(avg_g))) - 1) * 100
                color = "normal" if k_val > 0 else "inverse"
                
                ck1, ck2 = st.columns(2)
                with ck1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
                with ck2: st.metric("💵 기준 환율", f"{ex:,.1f}원")
                
                # 차트 기록
                now = datetime.now().strftime('%H:%M:%S')
                st.session_state['logs'].append({"시간": now, "김프": k_val})
                if len(st.session_state['logs']) > 30: st.session_state['logs'].pop(0)
                
                st.write("---")
                st.subheader("📉 김프 실시간 변화")
                st.line_chart(pd.DataFrame(st.session_state['logs']).set_index("시간"))
            
            st.caption(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 갱신)")
            
            with st.sidebar:
                st.success("⚓ 아르 아빠님 접속 중")
                if st.button("안전 로그아웃"):
                    st.session_state['is_auth'] = False
                    st.rerun()
            
            time.sleep(10); st.rerun()
        else:
            st.info("🎣 유닛 737이 전 세계 거래소를 돌며 데이터를 낚는 중입니다...")
            time.sleep(3); st.rerun()
