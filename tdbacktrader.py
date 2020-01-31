from datetime import datetime
import tdlib as py
import numpy as np

if __name__ == '__main__':
    obj = py.TDTrader()
    accinfo = obj.get_account()

    quote = obj.get_history('TQQQ')
    print(quote.tail(10))
    mask = (quote['datetime'] > '2019-07-20 08:00:00') & (quote['datetime'] <= '2019-08-01 23:00:00')
    quote = quote.loc[mask]
    quote.set_index('datetime', inplace=True)

    quote = quote.resample('5T').agg(
        {'close':'last', 'high':np.max, 'low':np.min, 'open':'first', 'volume':np.sum})
    quote = quote.dropna()
    obj.backtradelogic(quote)
    print("P/L : ", 100 * obj.pl / obj.capital)
