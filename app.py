import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1. 🌟 페이지 설정
st.set_page_config(page_title="아르아빠 USDT AI", layout="wide", initial_sidebar_state="collapsed")

# 2. 🎨 [디자인] 초고대비 프리미엄 & 모바일 배지 박멸
def apply_final_perfection_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap');
        header, footer, #MainMenu { visibility: hidden; display: none !important; }
        .stAppDeployButton, [data-testid="stToolbar"] { display: none !important; }
        .stApp { background-color: #000000 !important; color: #ffffff !important; top: -50px; }
        
        /* 지표 숫자 (형광 화이트) */
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important; font-size: clamp(1.4rem, 6vw, 2.5rem) !important;
            font-weight: 900 !important; text-shadow: 2px 2px 4px rgba(0,0,0,1);
        }
        [data-testid="stMetricLabel"] p { color: #26A17B !important; font-weight: 700 !important; font-size: 0.9rem !important; }
        
        .main-title { text-align: center; color: #26A17B; font-family: 'Black Han Sans', sans-serif; font-size: clamp(1.6rem, 7vw, 2.3rem); margin-bottom: 20px; }
        .trade-card { background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
        div.stButton > button { background-color: #26A17B !important; color: white !important; font-weight: 700; border-radius: 10px; border: none; height: 3.5em; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

# 3. 💰 [집요한 엔진] 바이낸스 및 해외 시세 낚시
def fetch_global_price(target):
    h = {'User-Agent': 'Mozilla/5.0'}
    try:
        if target == "up": return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        if target == "ex": return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
        if target == "ok": return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        
        if target == "bn":
            # 바이낸스가 안 되면 즉시 쿠코인이나 대체 서버 시도
            urls = ["https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", 
                    "https://api1.binance.com/api/v3/ticker/price?symbol=USDTUSD",
                    "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=USDT-USDT"]
            for url in urls:
                try:
                    res = requests.get(url, headers=h, timeout=3).json()
                    return float(res['price'] if 'price' in res else res['data']['price'])
                except: continue
    except: return None

# 세션 초기화 (데이터 보존)
for key, val in {'auth': False, 'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'menu': 'kimp',
                 'realized_pnl': 0.0, 'total_fees': 0.0, 'wins': 0, 'losses': 0, 'history': [], 'trade_logs': []}.items():
    if key not in st.session_state: st.session_state[key] = val

apply_final_perfection_style()

# 🛡️ 로그인 (플레이스홀더 적용)
main_area = st.empty()
if not st.session_state['auth']:
    with main_area.container():
        st.markdown("<br><br><div style='background-color:#26A17B; padding:30px; border-radius:20px; color:white; text-align:center;'><h1>AI 오두막</h1><p>Ar & Or & Unit 737 Private Terminal</p></div>", unsafe_allow_html=True)
        pw = st.text_input("열쇠 (PW)", type="password", key="login_v32")
        if st.button("시스템 접속"):
            if pw == "aror737":
                st.session_state['auth'] = True
                main_area.empty(); time.sleep(0.15); st.rerun()
            else: st.error("열쇠 불일치")
    st.stop()

# ---------------------------------------------------------
# 📈 메인 대시보드 (로그인 후)
# ---------------------------------------------------------

# 상단 내비게이션
m1, m2 = st.columns(2)
with m1: 
    if st.button("📊 실시간 김프", key="nav_kimp"): st.session_state['menu'] = "kimp"
with m2: 
    if st.button("💹 가상 매매 & 분석", key="nav_trade"): st.session_state['menu'] = "trade"

# 데이터 로드
up, bn, ok, ex = fetch_global_price("up"), fetch_global_price("bn"), fetch_global_price("ok"), fetch_global_price("ex")
bn_k = (bn * ex) if (bn and ex) else None
ok_k = (ok * ex) if (ok and ex) else None
avg_list = [p for p in [bn_k, ok_k] if p]
global_avg = sum(avg_list)/len(avg_list) if avg_list else 0
k_val = ((up / global_avg) - 1) * 100 if (up and global_avg) else 0.0
kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime('%H:%M:%S')

if st.session_state['menu'] == "kimp":
    st.markdown("<div class='main-title'>⚓ USDT 김프 현황</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🇰🇷 업비트", f"{up:,.0f}원" if up else "대기")
    with c2: st.metric("🔶 바이낸스", f"{bn_k:,.0f}원" if bn_k else "대기")
    with c3: st.metric("🖤 OKX", f"{ok_k:,.0f}원" if ok_k else "대기")
    with c4: st.metric("📊 김프", f"{k_val:.2f}%", delta=f"{k_val:.2f}%")
    
    st.write("---")
    st.session_state['history'].append({"시간": now, "김프": k_val})
    if len(st.session_state['history']) > 30: st.session_state['history'].pop(0)
    st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))
    st.caption(f"환율: {ex:,.1f}원 | 갱신: {now}")
    time.sleep(15); st.rerun()

else:
    st.markdown("<div class='main-title'>💹 가상 매매 & 분석 리포트</div>", unsafe_allow_html=True)
    
    # 1. 투자 분석 요약
    total_t = st.session_state['wins'] + st.session_state['losses']
    win_r = (st.session_state['wins'] / total_t * 100) if total_t > 0 else 0
    
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown(f"<div class='trade-card'><b>누적 확정 수익</b><br><span style='font-size:1.3rem;'>{st.session_state['realized_pnl']:,.0f}원</span></div>", unsafe_allow_html=True)
    with s2: st.markdown(f"<div class='trade-card'><b>매매 승률</b><br><span style='font-size:1.3rem;'>{win_r:.1f}% ({total_t}회)</span></div>", unsafe_allow_html=True)
    with s3: st.markdown(f"<div class='trade-card'><b>누적 수수료</b><br><span style='font-size:1.3rem;'>{st.session_state['total_fees']:,.0f}원</span></div>", unsafe_allow_html=True)

    # 2. 지갑 및 실시간 손익
    cur_pnl = (st.session_state['qty'] * up) - (st.session_state['qty'] * st.session_state['avg']) if (st.session_state['qty'] > 0 and up) else 0
    pnl_p = (cur_pnl / (st.session_state['qty'] * st.session_state['avg']) * 100) if (st.session_state['qty'] > 0 and st.session_state['avg'] > 0) else 0
    
    v1, v2 = st.columns(2)
    with v1: st.markdown(f"<div class='trade-card'><h3>💳 내 지갑</h3><p>현금: {st.session_state['cash']:,.0f}원</p><p>보유: {st.session_state['qty']:.2f} USDT</p><p>평단: {st.session_state['avg']:,.0f}원</p></div>", unsafe_allow_html=True)
    with v2:
        p_color = "#ff4b4b" if cur_pnl > 0 else "#1c83e1" if cur_pnl < 0 else "#ffffff"
        st.markdown(f"<div class='trade-card'><h3>📊 미실현 손익</h3><h2 style='color:{p_color};'>{cur_pnl:,.0f}원 ({pnl_p:+.2f}%)</h2><p>현재가: {up:,.0f}원</p></div>", unsafe_allow_html=True)

    st.write("---")
    amt = st.number_input("매수 금액(원)", min_value=0.0, max_value=st.session_state['cash'], step=100000.0, value=1000000.0, key="trade_amt")
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚀 매수 실행"):
            if up and amt > 0:
                fee = amt * 0.0005; st.session_state['total_fees'] += fee
                net = amt - fee; nq = net / up
                st.session_state['avg'] = ((st.session_state['qty'] * st.session_state['avg']) + net) / (st.session_state['qty'] + nq)
                st.session_state['qty'] += nq; st.session_state['cash'] -= amt
                st.session_state['trade_logs'].append({"시간": now, "유형": "매수", "금액": amt, "단가": up})
                st.rerun()
    with b2:
        if st.button("💰 전량 매도"):
            if up and st.session_state['qty'] > 0:
                val = st.session_state['qty'] * up; fee = val * 0.0005
                st.session_state['total_fees'] += fee
                trade_p = (val - fee) - (st.session_state['qty'] * st.session_state['avg'])
                st.session_state['realized_pnl'] += trade_p
                if trade_p > 0: st.session_state['wins'] += 1
                else: st.session_state['losses'] += 1
                st.session_state['cash'] += (val - fee)
                st.session_state['trade_logs'].append({"시간": now, "유형": "매도", "금액": val, "단가": up})
                st.session_state['qty'] = 0; st.session_state['avg'] = 0; st.rerun()

    if st.session_state['trade_logs']:
        with st.expander("📜 상세 거래 로그"): st.table(pd.DataFrame(st.session_state['trade_logs']).iloc[::-1].head(10))

with st.sidebar:
    if st.button("🚪 안전 로그아웃"): st.session_state['auth'] = False; st.rerun()
