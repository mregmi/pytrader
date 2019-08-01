import tdlib as py
import pandas as pd
import time
from datetime import datetime, timedelta

import time

if __name__ == '__main__':
    obj = py.TDTrader()
    #accinfo = obj.get_account()
    quote = obj.get_quote("JNUG")
    now = datetime.now()
    while now.minute % 5 != 0:
        time.sleep(0.2)

    print('Program is starting', datetime.now())
    tm = datetime.now() - timedelta(minutes=5)
    min = tm.minute
    candle = pd.DataFrame()
    while True:
        dt = datetime.now()
        start = time.time()
        q1 = obj.get_quote("JNUG")
        quote = quote.append(q1)
        #print(quote)
        if tm < dt - timedelta(minutes=5):
            quote['datetime'] = dt#pd.to_datetime(quote['quoteTimeInLong'], unit='ms')
            quote.set_index('datetime', inplace=True)
            quote['mark'] = quote['mark'].astype(float)
            candle = candle.append(quote['mark'].resample('5T').ohlc(), sort=False)
            #print('Shuld be here every 5 mins ', dt, '\n')
            if dt > datetime(dt.year, dt.month, dt.day, 6, 30) and dt <= datetime(dt.year, dt.month, dt.day, 13, 2):
                obj.tradelogic(candle, dt)
            tm = dt
        time.sleep(2 - (time.time() - start))

    print("P/L : ", 100 * obj.pl / obj.capital)
