def fetch_prices():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    data = {"up": None, "bn": None, "ok": None}
    
    # 1. 업비트 (국내)
    try:
        data["up"] = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=5).json()[0]['trade_price'])
    except Exception as e:
        st.error(f"업비트 통신 에러: {e}")

    # 2. 바이낸스 (해외) - 엔드포인트 여러 개 시도
    bn_urls = ["https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", 
               "https://api1.binance.com/api/v3/ticker/price?symbol=USDTUSD",
               "https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD"]
    for url in bn_urls:
        try:
            res = requests.get(url, headers=h, timeout=5)
            if res.status_code == 200:
                data["bn"] = float(res.json()['price'])
                break
        except:
            continue
            
    # 3. OKX (해외)
    try:
        res = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", headers=h, timeout=5)
        if res.status_code == 200:
            data["ok"] = float(res.json()['data'][0]['last'])
    except Exception as e:
        pass # OKX가 안되더라도 바이낸스가 있으면 작동함

    return data
