import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 고대비 & 4열 레이아웃 스타일
def apply_perfect_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 (쨍한 화이트) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important; font-size: clamp(1.2rem, 5vw, 2.2rem) !important;
            font-weight: 900 !important; text-shadow: 1px 1px 2px rgba(0,0,0,1);
        }
        
        /* 지표 이름 (민트색) */
        [data-testid="stMetricLabel"] p {
            color: #26A17B !important; font-size: clamp(0.7rem, 3vw, 0.9rem) !important; font-weight: 700 !important;
        }

        .main-title { text-align: center; color: #26A17B; font-weight: 900; font-size: clamp(1.5rem, 6vw, 2.2rem); margin-bottom: 20px; }
        [data-testid="stMetric"] { background-color: #1e2129 !important; border-top: 4px solid #26A17B !important; padding: 12px !important; border-radius: 10px !important; }
        
        /* 안내 배너 */
        .base-info { background-color: #26A17B; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: 700; font-size: 0.9rem; }
        
        /* 버튼 디자인 */
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 8px; border: none; height: 3.2em; }
        
        /* 가상 매매 카드 */
        .trade-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 15px; color: white; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 데이터 수집 엔진
def get_safe_price(exchange):
    try:
        timeout = 5
        if exchange == "up": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=timeout).json()[0]['trade_price'])
        if exchange == "bn": return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=timeout).json()['price'])
        if exchange == "ok": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=timeout).json()['data'][0]['last'])
        if exchange == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=timeout).json()['rates']['KRW'])
    except: return None

# 세션 관리
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'menu' not in st.session_state: st.session_state['menu'] = "kimp"
if 'cash' not in st.session_state: st.session_state['cash'] = 10000000.0
if 'qty' not in st.session_state: st.session_state['qty'] = 0.0
if 'avg' not in st.session_state: st.session_state['avg'] = 0.0
if 'history' not in st.session_state: st.session_state['history'] = []
if 'trade_logs' not in st.session_state: st.session_state['trade_logs'] = []

apply_perfect_style()

# 🛡️ 로그인 검문소
main_placeholder = st.empty()
with main_placeholder.container():
    if not st.session_state['auth']:
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private Terminal</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v29")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_placeholder.empty(); time.sleep(0.15); st.rerun()
            else: st.error("틀렸습니다.")
        st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드
# ---------------------------------------------------------

# 상단 내비게이션
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 실시간 김프", use_container_width=True): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 가상 매매", use_container_width=True): st.session_state['menu'] = "trade"

# 공통 데이터 수집
up = get_safe_price("up"); bn = get_safe_price("bn"); ok = get_safe_price("ok"); ex = get_safe_price("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None

# 김프 계산 로직
avg_list = []; sources = []
if bn_k: avg_list.append(bn_k); sources.append("Binance")
if ok_k: avg_list.append(ok_k); sources.append("OKX")
global_avg = sum(avg_list)/len(avg_list) if avg_list else 0
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0
kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime('%H:%M:%S')

# [화면 1: 실시간 김프]
if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    if sources:
        st.markdown(f"<div class='base-info'>📢 비교 기준: {' + '.join(sources)} 평균 ({global_avg:,.0f}원)</div>", unsafe_allow_html=True)
    
    # 4열 배치
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원" if up else "대기")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
    with c4: st.metric("📊 실시간 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    st.caption(f"기준 환율: {ex:,.1f}원 | 갱신 시간: {now} (15초 자동)")
    time.sleep(15); st.rerun()

# [화면 2: 가상 매매 복구 완료]
else:
    st.markdown("<div class='main-title'>💹 가상 매매 Beta</div>", unsafe_allow_html=True)
    
    # 수익률 계산
    cur_val = st.session_state['qty'] * up if up else 0
    pnl = cur_val - (st.session_state['qty'] * st.session_state['avg']) if st.session_state['qty'] > 0 else 0
    pnl_p = (pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0 and st.session_state['avg'] > 0) else 0
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>가용 현금: {st.session_state['cash']:,.0f}원</p><p>보유 수량: {st.session_state['qty']:.2f} USDT</p><p>평균 단가: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with col_v2:
        p_color = "#ff4b4b" if pnl > 0 else "#1c83e1" if pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📈 투자 손익</h3><h2 style='color:{p_color};'>{pnl:,.0f}원 ({pnl_p:+.2f}%)</h2><p>현재가: {up:,.0f}원 | 김프: {k_val:.2f}%</p></div>", unsafe_allow_html=True)

    st.write("---")
    buy_amt = st.number_input("매수 금액 입력 (원)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0, value=1000000.0)
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚀 매수 실행", use_container_width=True):
            if up and buy_amt > 0:
                fee = buy_amt * 0.0005
                net_amt = buy_amt - fee
                new_q = net_amt / up
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + net_amt) / (st.session_state['qty'] + new_q)
                st.session_state['qty'] += new_q
                st.session_state['cash'] -= buy_amt
                st.session_state['trade_logs'].append({"시간": now, "유형": "매수", "금액": buy_amt, "단가": up})
                st.success("매수 완료!"); time.sleep(1); st.rerun()
    with b2:
        if st.button("💰 전량 매도", use_container_width=True):
            if up and st.session_state['qty'] > 0:
                sell_val = st.session_state['qty'] * up
                fee = sell_val * 0.0005
                st.session_state['cash'] += (sell_val - fee)
                st.session_state['trade_logs'].append({"시간": now, "유형": "매도", "금액": sell_val, "단가": up})
                st.session_state['qty'] = 0; st.session_state['avg'] = 0
                st.success("전량 매도 완료!"); time.sleep(1); st.rerun()

    if st.session_state['trade_logs']:
        with st.expander("📜 최근 거래 내역 (10건)"):
            st.table(pd.DataFrame(st.session_state['trade_logs']).iloc[::-1].head(10))

with st.sidebar:
    if st.button("🚪 안전 로그아웃"):
        st.session_state['auth'] = False; st.rerun()
