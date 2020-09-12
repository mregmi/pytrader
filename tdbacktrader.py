from datetime import datetime
import tdlib as py
import numpy as np

if __name__ == '__main__':
    symbol = 'TQQQ'
    obj = py.TDTrader(symbol, 10000)
    accinfo = obj.get_account()
    quote = obj.get_history(symbol)
    mask = (quote['datetime'] > '2020-09-02 04:00:00') & (quote['datetime'] <= '2020-09-07 17:00:00')
    quote = quote.loc[mask]
    quote.set_index('datetime', inplace=True)
    #print(quote)
    #quit()

    quote1 = quote.resample('5T').agg(
        {'close':'last', 'high':np.max, 'low':np.min, 'open':'first', 'volume':np.sum})
    quote1 = quote1.dropna()
    quote5 = quote.resample('1T').agg(
        {'close':'last', 'high':np.max, 'low':np.min, 'open':'first', 'volume':np.sum})
    quote5 = quote5.dropna()
    obj.backtradelogic(quote1, quote5, symbol, obj.capital)
    print("P/L : ", 100 * obj.pl / obj.capital)
