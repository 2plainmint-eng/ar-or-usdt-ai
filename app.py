import streamlit as st
import requests
import pandas as pd
import time

# 1. 🌟 기본 설정
st.set_page_config(page_title="USDT AI 오두막", layout="wide")

# 2. 💰 데이터 엔진 (가장 확실한 경로)
def get_data():
    res = {"up": 0, "bn": 0, "ok": 0, "ex": 1380, "success": False}
    try:
        # 업비트
        up_r = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()
        res["up"] = float(up_r[0]['trade_price'])
        
        # 환율
        ex_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        res["ex"] = float(ex_r['rates']['KRW'])
        
        # 바이낸스
        try:
            bn_r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", timeout=5).json()
            res["bn"] = float(bn_r['price'])
            res["success"] = True
        except: pass
        
        # OKX
        try:
            ok_r = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=5).json()
            res["ok"] = float(ok_r['data'][0]['last'])
            res["success"] = True
        except: pass
        
    except Exception as e:
        st.error(f"데이터 수집 중 오류: {e}")
    return res

# 3. 세션 초기화
for key, val in {'cash': 10000000.0, 'qty': 0.0, 'avg': 0.0, 'history': []}.items():
    if key not in st.session_state: st.session_state[key] = val

# 4. 메인 화면 레이아웃
st.title("⚓ USDT 실시간 터미널")

d = get_data()
# 해외 가격 평균 계산
foreign_list = [p for p in [d['bn'], d['ok']] if p > 0]
f_avg = (sum(foreign_list) / len(foreign_list)) if foreign_list else 1.0
f_price_krw = f_avg * d['ex']
kimp = ((d['up'] / f_price_krw) - 1) * 100 if f_price_krw > 0 else 0

# --- 상단 지표 ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("🇰🇷 업비트", f"{d['up']:,}원")
c2.metric("🌎 해외평균", f"{f_price_krw:,.1f}원")
c3.metric("📊 김프", f"{kimp:.2f}%")
c4.metric("💵 환율", f"{d['ex']:,}원")

st.write("---")

# --- 가상 매매 섹션 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💳 내 지갑")
    st.write(f"**보유 현금:** {st.session_state['cash']:,.0f}원")
    st.write(f"**보유 수량:** {st.session_state['qty']:.2f} USDT")
    st.write(f"**내 평단가:** {st.session_state['avg']:,.1f}원")

with col_right:
    st.subheader("🛒 주문")
    trade_q = st.number_input("거래 수량 입력", value=1000.0, step=100.0)
    
    b1, b2 = st.columns(2)
    if b1.button("🚀 즉시 매수"):
        cost = trade_q * d['up'] * 1.0005 # 수수료 포함
        if st.session_state['cash'] >= cost:
            total_cost = (st.session_state['qty'] * st.session_state['avg']) + (trade_q * d['up'])
            st.session_state['qty'] += trade_q
            st.session_state['avg'] = total_cost / st.session_state['qty']
            st.session_state['cash'] -= cost
            st.rerun()
        else: st.error("잔액 부족")
        
    if b2.button("💸 즉시 매도"):
        if st.session_state['qty'] >= trade_q:
            st.session_state['cash'] += (trade_q * d['up'] * 0.9995)
            st.session_state['qty'] -= trade_q
            if st.session_state['qty'] < 0.1: st.session_state['avg'] = 0
            st.rerun()
        else: st.error("수량 부족")

# --- 그래프 ---
st.write("---")
st.session_state['history'].append({"시간": time.strftime('%H:%M:%S'), "김프": kimp})
if len(st.session_state['history']) > 20: st.session_state['history'].pop(0)
st.line_chart(pd.DataFrame(st.session_state['history']).set_index("시간"))

if st.button("🔄 수동 새로고침"):
    st.rerun()
