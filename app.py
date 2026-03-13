# 3. 💰 데이터 엔진 (바이낸스 특수 보강 버전)
def fetch_now(target):
    # 브라우저인 척 위장하는 헤더
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        if target == "upbit": 
            return float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-USDT", timeout=3).json()[0]['trade_price'])
        
        elif target == "binance": 
            # 1순위: 바이낸스 api3 (가장 안정적)
            try:
                return float(requests.get("https://api3.binance.com/api/v3/ticker/price?symbol=USDTUSD", headers=headers, timeout=3).json()['price'])
            except:
                # 2순위: 바이낸스 일반 api 우회
                try:
                    return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSD", headers=headers, timeout=3).json()['price'])
                except:
                    # 3순위: 바이낸스가 죽었을 때 쿠코인(KuCoin)에서 낚아오기 (보험)
                    return float(requests.get("https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=USDT-USDT", timeout=3).json()['data']['price'])
        
        elif target == "okx":
            return float(requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD", timeout=3).json()['data'][0]['last'])
        
        elif target == "ex": 
            return float(requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3).json()['rates']['KRW'])
    except: 
        return None
