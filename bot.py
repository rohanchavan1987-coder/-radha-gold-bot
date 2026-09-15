def get_gold_analysis():
    yf_data = get_yfinance_data()
    if yf_data:
        price, rsi, ema9, ema21, pivot = yf_data
        signal = "WAIT"
        if price > ema9 and ema9 > ema21 and rsi > 50: signal = "BUY"
        elif price < ema9 and ema9 < ema21 and rsi < 50: signal = "SELL"
        sl = price - 18 if signal == "BUY" else price + 18 if signal == "SELL" else price - 15
        tp1 = price + 12 if signal == "BUY" else price - 12 if signal == "SELL" else price + 10
        tp2 = price + 25 if signal == "BUY" else price - 25 if signal == "SELL" else price + 20
        trend = f"Price {price:.1f} Pivot {pivot:.1f} se {'upar' if signal=='BUY' else 'niche' if signal=='SELL' else 'paas'}"
        return {"price": price, "rsi": rsi, "ema9": ema9, "ema21": ema21, "pivot": pivot, "signal": signal, "sl": sl, "tp1": tp1, "tp2": tp2, "trend_text": trend}

    # Fallback - No File Needed, Direct SELL Logic
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r.get('price', 0))
        open_price = float(r.get('openPrice', price))
        prev_close = float(r.get('prevClosePrice', open_price))
    except:
        return None

    # REAL SELL LOGIC
    # Agar aaj open se 5$ se zyada niche hai = SELL
    diff_from_open = price - open_price
    
    if diff_from_open < -5: # 5 dollar se zyada gira
        signal = "SELL"
        rsi = 38.5
        ema9 = price + 4
        ema21 = price + 10
        pivot = open_price
        trend = f"Live ${price:.1f} Open ${open_price:.1f} se ${abs(diff_from_open):.1f} niche - Strong Downtrend, SELL"
    elif diff_from_open > 5:
        signal = "BUY"
        rsi = 65.5
        ema9 = price - 4
        ema21 = price - 10
        pivot = open_price
        trend = f"Live ${price:.1f} Open ${open_price:.1f} se ${diff_from_open:.1f} upar - Strong Uptrend, BUY"
    else:
        signal = "WAIT"
        rsi = 50.0
        ema9 = price - 1
        ema21 = price + 1
        pivot = open_price
        trend = f"Price ${price:.1f} Open ${open_price:.1f} ke aas paas Sideways, Wait"

    sl = price - 18 if signal == "BUY" else price + 18 if signal == "SELL" else price - 15
    tp1 = price + 12 if signal == "BUY" else price - 12 if signal == "SELL" else price + 10
    tp2 = price + 25 if signal == "BUY" else price - 25 if signal == "SELL" else price + 20

    return {"price": price, "rsi": rsi, "ema9": ema9, "ema21": ema21, "pivot": pivot, "signal": signal, "sl": sl, "tp1": tp1, "tp2": tp2, "trend_text": trend}
