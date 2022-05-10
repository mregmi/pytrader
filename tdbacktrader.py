from datetime import datetime
from collections import OrderedDict
import sys
import tdlib as py
import numpy as np

if __name__ == '__main__':
    ohlc_dict = {                                                                                                             
        'open': 'first',                                                                                                    
        'high': 'max',                                                                                                       
        'low': 'min',                                                                                                        
        'close': 'last',                                                                                                    
        'volume': 'sum',
    }
    symbol = sys.argv[1]#'TSLA'
    obj = py.TDTrader(symbol, 10000)
    accinfo = obj.get_account()
    quote = obj.get_history(symbol)
    mask = (quote['datetime'] > '2022-05-04 04:00:00') & (quote['datetime'] <= '2022-05-04 17:00:00')
    quote = quote.loc[mask]
    quote.set_index('datetime', inplace=True)
    #print(quote)
    #quit()

    quote1 = quote.resample('1Min').agg(OrderedDict(ohlc_dict))
    quote1 = quote1.dropna()
    quote5 = quote.resample('5Min').agg(OrderedDict(ohlc_dict))
    quote5 = quote5.dropna()
    obj.backtradelogic(quote1, quote5, symbol, obj.capital)
    print("P/L : ", 100 * obj.pl / obj.capital)
