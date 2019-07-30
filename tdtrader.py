import tdlib as py
import pandas as pd
from datetime import datetime, timedelta

import time

if __name__ == '__main__':
    obj = py.TDTrader()
    #accinfo = obj.get_account()
    quote = obj.get_quote("JNUG")
    while datetime.now().minute % 5 != 0:
        time.sleep(1)
    print('Program is starting', datetime.now())
    tm = datetime.now() - timedelta(minutes=5)
    min = tm.minute
    candle = pd.DataFrame()
    while True:
        q1 = obj.get_quote("JNUG")
        quote = quote.append(q1)
        #print(quote)
        dt = datetime.now()
        if tm < dt - timedelta(minutes=5):
            quote['datetime'] = dt#pd.to_datetime(quote['quoteTimeInLong'], unit='ms')
            quote.set_index('datetime', inplace=True)
            quote['mark'] = quote['mark'].astype(float)
            candle = candle.append(quote['mark'].resample('5T').ohlc(), sort=False)
            print('Shuld be here every 5 mins ', dt, '\n')
            if dt > datetime(dt.year, dt.month, dt.day, 6, 30) and dt <= datetime(dt.year, dt.month, dt.day, 13, 00):
                obj.tradelogic(candle, dt)
            tm = dt
        time.sleep(1)

    print("P/L : ", 100 * obj.pl / obj.capital)
