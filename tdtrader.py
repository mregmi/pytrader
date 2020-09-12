import tdlib as py
import pandas as pd
import time
from datetime import datetime, timedelta

import time

if __name__ == '__main__':
    symbol = 'SQQQ'
    obj = py.TDTrader(symbol, 40000)
    #accinfo = obj.get_account()
    quote = obj.get_quote(symbol)
    #while datetime.now().minute % 5 != 0:
    #    time.sleep(0.1)
        
    print('Program is starting', datetime.now())
    tm = datetime.now() - timedelta(minutes=1)
    min = tm.minute
    candle = pd.DataFrame()
    while True:
        dt = datetime.now()
        start = time.time()
        try:
            q1 = obj.get_quote(symbol)
            #print(q1)
            price = q1.iloc[0]['mark']
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        quote = quote.append(q1)

        if tm < dt - timedelta(minutes=5):
            quote['datetime'] = dt#pd.to_datetime(quote['quoteTimeInLong'], unit='ms')
            quote.set_index('datetime', inplace=True)
            quote['mark'] = quote['mark'].astype(float)
            candle = candle.append(quote['mark'].resample('5T').ohlc(), sort=False)
            #print('Shuld be here every 1 mins ', candle, '\n')
            if dt > datetime(dt.year, dt.month, dt.day, 6, 30) and dt <= datetime(dt.year, dt.month, dt.day, 13, 0):
                obj.tradelogic(candle, dt)
            if dt > datetime(dt.year, dt.month, dt.day, 12, 58) and dt < datetime(dt.year, dt.month, dt.day, 13, 58):
                obj.doClosingSell(price, dt)
                break
            tm = dt
        if obj.mustSell():
            obj.doSell(price, dt)

        delta = time.time() - start
        if delta < 20:
            time.sleep(30 - delta)

    print("P/L : ", 100 * obj.pl / obj.capital)
