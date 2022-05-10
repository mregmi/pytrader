import tdlib as py
import pandas as pd
import time
from datetime import datetime, timedelta
from collections import OrderedDict

import time

if __name__ == '__main__':
    symbol = 'SQQQ'
    ohlc_dict = {                                                                                                             
        'open': 'first',                                                                                                    
        'high': 'max',                                                                                                       
        'low': 'min',                                                                                                        
        'close': 'last',                                                                                                    
        'volume': 'sum',
    }

    obj = py.TDTrader(symbol, 40000)
    #accinfo = obj.get_account()
    quote = obj.get_quote(symbol)
    #while datetime.now().minute % 5 != 0:
    #    time.sleep(0.1)
        
    print('Program is starting', datetime.now())
    tm = datetime.now() - timedelta(minutes=1)
    min = tm.minute
    count = 0
    candle1 = pd.DataFrame()
    candle5 = pd.DataFrame()
    while True:
        dt = datetime.now()
        start = time.time()
        try:
            q1 = obj.get_quote(symbol)
            #print(q1)
            obj.price = q1.iloc[0]['mark']
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        quote = pd.concat([quote, q1])
        #print(quote)

        if tm < dt - timedelta(minutes=1):
            quote['datetime'] = dt#pd.to_datetime(quote['quoteTimeInLong'], unit='ms')
            quote.set_index('datetime', inplace=True)
            quote['mark'] = quote['mark'].astype(float)

            candle5 = pd.concat([candle5, quote['mark'].resample("5Min").apply(ohlc_dict)])
            candle1 = pd.concat([candle1, quote['mark'].resample("1Min").apply(ohlc_dict)])
            if count < 5 and len(candle5) > 1:
                candle5.drop(candle5.tail(1).index, inplace=True)
            else:
                count = 0
            #print("1 Min ", len(candle1), candle1.tail(2))
            #print("5 Min ", len(candle5), candle5.tail(2))
            if dt > datetime(dt.year, dt.month, dt.day, 6, 30) and dt <= datetime(dt.year, dt.month, dt.day, 13, 0):
                obj.tradelogic(candle1, candle5, dt)
            if dt > datetime(dt.year, dt.month, dt.day, 12, 58) and dt < datetime(dt.year, dt.month, dt.day, 13, 58):
                obj.doClosingSell(obj.price, dt)
                break
            tm = dt
            count = count + 1

        if obj.mustSell():
            obj.doSell(obj.price, dt)

        delta = time.time() - start
        #print(delta)
        if delta < 10:
            time.sleep(10 - delta)

    print("P/L : ", 100 * obj.pl / obj.capital)
