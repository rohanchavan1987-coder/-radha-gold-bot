import requests

def get_live_gold_price():
    try:
        # Real-time Gold API - TradingView jaisa live price
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r['price'])  # Ye ab 4190.xx dega
        return price
    except:
        # Backup API
        try:
            r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10).json()
            # XAU price nikalna
            for item in r['items']:
                if item['curr'] == 'XAU':
                    return float(item['xauPrice'])
        except:
            return 4190.0  # fallback
