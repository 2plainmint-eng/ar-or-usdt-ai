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
        
        /* 제목: 모바일 한 줄 고정 */
        .main-title { 
            text-align: center; color: #26A17B; font-weight: 700; 
            font-size: 24px; white-space: nowrap; margin-bottom: 20px;
        }
        
        /* 로그인 카드 */
        .login-card { background-color: #26A17B; padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
        
        /* 지표 박스 */
        .metric-card { 
            background-color: white; padding: 15px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #26A17B;
            text-align: center; margin-bottom: 10px;
        }
        
        /* 버튼 */
        div.stButton > button { background-color: #26A17B; color: white; border-radius: 10px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. [데이터] 개별 낚시 엔진 (안전성 극대화) ---
def get_single_price(url, keys):
    try:
        res = requests.get(url, timeout=5).json()
        for k in keys:
            res = res[k]
        return float(res)
    except:
        return None

# --- 3. 시스템 설정 ---
if 'auth_done' not in st.session_state: st.session_state['auth_done'] = False
if 'kimp_history' not in st.session_state: st.session_state['kimp_history'] = []

apply_premium_style()

# --- [화면 1: 로그인] ---
if not st.session_state['auth_done']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([0.05, 0.9, 0.05])
    with col:
        st.markdown("<div class='login-card'><h1>AI 오두막</h1><p>Ar & Or & Unit 737</p></div>", unsafe_allow_html=True)
        pw = st.text_input("오두막 열쇠 (PW)", type="password")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth_done'] = True
                st.rerun()
            else: st.error("열쇠가 맞지 않습니다.")

# --- [화면 2: 대시보드] ---
else:
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    
    # 각개전투 데이터 수집
    up_krw = get_single_price("https://api.upbit.com/v1/ticker?markets=KRW-USDT", [0, 'trade_price'])
    ex_rate = get_single_price("https://api.exchangerate-api.com/v4/latest/USD", ['rates', 'KRW'])
    bn_usd = get_single_price("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", ['price'])
    ok_usd = get_single_price("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", ['data', 0, 'last'])

    # 데이터가 하나라도 있으면 화면 구성
    if up_krw or bn_usd or ok_usd:
        # 한화 변환
        bn_krw = (bn_usd * ex_rate) if (bn_usd and ex_rate) else None
        ok_krw = (ok_usd * ex_rate) if (ok_usd and ex_rate) else None
        
        # 상단 비교 지표 (3열)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🇰🇷 업비트", f"{up_krw:,.0f}원" if up_krw else "대기중")
        with c2: st.metric("🔶 바이낸스", f"{bn_krw:,.0f}원" if bn_krw else "대기중")
        with c3: st.metric("🖤 OKX", f"{ok_krw:,.0f}원" if ok_krw else "대기중")
        
        # 중앙 김프 계산
        st.write("---")
        avg_global = []
        if bn_krw: avg_global.append(bn_krw)
        if ok_krw: avg_global.append(ok_krw)
        
        if avg_global and up_krw:
            k_val = ((up_krw / (sum(avg_global)/len(avg_global))) - 1) * 100
            color = "normal" if k_val > 0 else "inverse"
            
            col_k1, col_k2 = st.columns(2)
            with col_k1: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%", delta_color=color)
            with col_k2: st.metric("💵 기준 환율", f"{ex_rate:,.1f}원" if ex_rate else "확인중")
            
            # 그래프 기록
            now = datetime.now().strftime('%H:%M:%S')
            st.session_state['kimp_history'].append({"시간": now, "김프": k_val})
            if len(st.session_state['kimp_history']) > 30: st.session_state['kimp_history'].pop(0)
            
            st.write("---")
            st.subheader("📉 김프 실시간 변화")
            df = pd.DataFrame(st.session_state['kimp_history'])
            st.line_chart(df.set_index("시간"))
        
        st.caption(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')} (10초 자동 감시)")
        
        with st.sidebar:
            st.success("⚓ 아르 아빠님 접속 중")
            if st.button("안전 로그아웃"):
                st.session_state['auth_done'] = False
                st.rerun()
                
        time.sleep(10); st.rerun()
    else:
        st.info("🎣 유닛 737이 전 세계 거래소에서 첫 고기를 낚는 중입니다... (약 5초 소요)")
        time.sleep(3); st.rerun()
