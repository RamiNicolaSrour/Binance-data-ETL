# requests calls apis,ppnadas deal with tbales, os foer system setting
import os
import requests
import pandas as pd

# use binance apis and coinmarket link to retrn asset details
BASE = "https://api.binance.us/api/v3"
cmc_url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
cmc_symbols = ['BTC','ETH','USDT']
CMC_API_KEY = 'xxxxxxxx'

# define functio to get details of assets from the coinmarketcap and build a table
def get_cmc():
    key = CMC_API_KEY
    if not key:
        raise ValueError("set cmc api variable first")
    r = requests.get(cmc_url, params={'symbol': ','.join(cmc_symbols)}, headers={'X-CMC_PRO_API_KEY': key})
    r.raise_for_status()
    data = r.json()['data']
    return pd.DataFrame([{
        'asset_symbol': s,
        'cmc_id':data[s][0]['id'],
        'asset_name': data[s][0].get('name'),
        'asset_type': data[s][0].get('category'),
        'logo_url': data[s][0].get('logo')
    } for s in cmc_symbols])

# ------
# exchange info
# call exchange market api and loop over the symbols and build tbale fomr specific columns
r = requests.get(f"{BASE}/exchangeInfo").json()
df_EI = pd.DataFrame([{'symbol':s['symbol'], 'base_asset': s['baseAsset'],
                       'quote_asset': s['quoteAsset'], 'base_asset_precision': s.get('baseAssetPrecision'), 'quote_asset_precision': s.get('quoteAssetPrecision'),
                       'status': s.get('status'), 'is_spot_trading_allowed': s.get('isSpotTradingAllowed')}
                       for s in r['symbols']])
print(df_EI.head())
#---------
# klines
# a function that request the candlessticks, retunr a table, convert times and numbers
def get_klines(symbol, interval='1d', limit=1000):
    raw = requests.get(f"{BASE}/klines",
                       params={'symbol':symbol, 'interval':interval, 'limit':limit}).json()
    cols = ['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
    df = pd.DataFrame(raw).iloc[:, :11]
    df.columns = cols
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    num = ['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'quote_asset_volume', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
    df[num] = df[num].astype(float)
    df.insert(0, 'symbol', symbol)
    df.insert(0, 'interval', interval)
    return df
symbols = ['BTCUSDT', 'ETHUSDT', 'ETHBTC'] 
intervals = ['1d', '5m', '1h', '15m']
df_klines = pd.concat([get_klines(s, i) for s in symbols for i in intervals], ignore_index=True)
print(df_klines.head())
#-------------------
# ticker 24h
# request last 24 hr, create captured at column for the time data exrtacted
data = requests.get(f"{BASE}/ticker/24hr").json()
df_ticker = pd.DataFrame(data)[['symbol', 'priceChangePercent', 'lastPrice',
                                'lastQty','openPrice', 'highPrice',
                                'lowPrice', 'volume', 'quoteVolume', 'openTime',
                                'closeTime', 'count']]
df_ticker = df_ticker.rename(columns={'priceChangePercent':'price_change_per', 'lastPrice':'last_price',
                     'lastQty':'last_qty', 'openPrice':'open_price', 'highPrice':'high_price',
                     'lowPrice':'low_price', 'volume':'volume', 'quoteVolume':'quote_volume',
                     'openTime':'open_time', 'closeTime':'close_time'})
df_ticker['open_time'] = pd.to_datetime(df_ticker['open_time'], unit='ms')
df_ticker['close_time'] = pd.to_datetime(df_ticker['close_time'], unit='ms')
num = df_ticker.columns.drop(['symbol', 'open_time', 'close_time'])
df_ticker[num] = df_ticker[num].astype(float)
df_ticker['captured_at'] = pd.Timestamp.now()
print(df_ticker.head(4))

#make the extract fucntion to fetch the three binace tbales to 2nd part
def extract():
    return df_EI, df_klines, df_ticker