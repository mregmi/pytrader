from datetime import datetime
import tdlib as py
import numpy as np

if __name__ == '__main__':
    obj = py.TDTrader()
    accinfo = obj.get_account()
    symbol = 'JNUG'
    quote = obj.get_history(symbol)
    mask = (quote['datetime'] > '2020-03-01 04:00:00') & (quote['datetime'] <= '2020-03-19 17:00:00')
    quote = quote.loc[mask]
    quote.set_index('datetime', inplace=True)
    #print(quote)
    #quit()

    quote = quote.resample('5T').agg(
        {'close':'last', 'high':np.max, 'low':np.min, 'open':'first', 'volume':np.sum})
    quote = quote.dropna()
    obj.backtradelogic(quote, symbol, obj.capital)
    print("P/L : ", 100 * obj.pl / obj.capital)
