import streamlit as st
import requests

# 1. 페이지 설정 (최상단)
st.set_page_config(page_title="USDT 복구 모드", layout="wide")

# 2. 간단한 스타일 (충돌 방지)
st.markdown("""<style>
    .reportview-container { background: #0e1117; }
    h1 { color: #26A17B; }
</style>""", unsafe_allow_html=True)

# 3. 세션 초기화
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# 4. 로그인 체크 (이게 안 뜨면 코드 실행 자체가 막힌 것임)
if not st.session_state['auth']:
    st.title("🛡️ 시스템 보안 접속")
    pw = st.text_input("열쇠를 입력하세요", type="password")
    if st.button("접속"):
        if pw == "aror737":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# 5. 메인 화면 (로그인 성공 시)
st.title("✅ 접속 성공")
st.write("이제 데이터를 불러옵니다...")

# 여기서부터 데이터 수집 로직 시작
try:
    up_price = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price']
    st.metric("업비트 현재가", f"{up_price:,.0f}원")
except Exception as e:
    st.error(f"데이터 연결 실패: {e}")

if st.button("로그아웃"):
    st.session_state['auth'] = False
    st.rerun()
