import tdlib as py
import pandas as pd
import time
from datetime import datetime, timedelta

import time

if __name__ == '__main__':
    obj = py.TDTrader()
    #accinfo = obj.get_account()
    quote = obj.get_quote("JNUG")
    while datetime.now().minute % 5 != 0:
        time.sleep(0.1)
        
    print('Program is starting', datetime.now())
    tm = datetime.now() - timedelta(minutes=5)
    min = tm.minute
    candle = pd.DataFrame()
    while True:
        dt = datetime.now()
        start = time.time()
        q1 = obj.get_quote("JNUG")
        price = q1.iloc[0]['mark']
        quote = quote.append(q1)

        if tm < dt - timedelta(minutes=5):
            quote['datetime'] = dt#pd.to_datetime(quote['quoteTimeInLong'], unit='ms')
            quote.set_index('datetime', inplace=True)
            quote['mark'] = quote['mark'].astype(float)
            candle = candle.append(quote['mark'].resample('5T').ohlc(), sort=False)
            #print('Shuld be here every 5 mins ', dt, '\n')
            if dt > datetime(dt.year, dt.month, dt.day, 6, 30) and dt <= datetime(dt.year, dt.month, dt.day, 13, 2):
                obj.tradelogic(candle, dt)
            tm = dt
        if obj.mustSell():
            obj.doSell(price, dt)

        delta = time.time() - start
        if delta < 2:
            time.sleep(2 - delta)

    print("P/L : ", 100 * obj.pl / obj.capital)
