from datetime import datetime, timedelta

import json
import pandas as pd
import numpy as np
import talib as ta
import time

import logging
logger = logging.getLogger()


class TraderAlgo:
    def __init__(self, symbol, capital):
        self.capital = capital
        self.symbol = symbol
        self.lastsar = 0
        self.lasthist = 0
        self.macdHist = 0
        self.sar = 0
        self.maxval = 0
        self.candles = 0
        self.Pprofit = 0
    
    def CalcAlgos(self, df, price):
        closep = df['close'].values
        high = df['high'].values
        low = df['low'].values

        #print(closep)
        # Ema 12 26
        self.emaslow = ta.EMA(closep, 12)
        self.emafast = ta.EMA(closep, 26)
#       df['EMASlow'] = emaslow
#       df['EMAHigh'] = emafast

        # MACD
        macd = ta.MACDEXT(closep, signalmatype=1)
        #print(macd)
#        df['MACD_val'] = macd[0]
#        df['MACD_Sig'] = macd[1]
        self.lasthist = self.macdHist
        self.macdHist = macd[2][-1]
        #print(self.lasthist, self.macdHist)

        #SAR
        self.lastsar = self.sar
        self.sar = ta.SAR(high, low, acceleration=0.02, maximum=0.2)[-1]
        #print(self.lastsar, self.sar)
        if price > self.maxval:
            self.maxval = price
        self.candles = self.candles + 1
        
    def GetBuySignal(self):
        if self.macdHist < 0.01:
            return False

        if self.macdHist - self.lasthist > 0.02 and (self.sar - self.lastsar) > 0.02:
            #print('Buy Signal: ', self.macdHist - self.lasthist, self.sar - self.lastsar)
            self.candles = 0
            return True
        
        return False

    def GetTotalProfit(self):
        return self.Pprofit
    
    def GetSellSignal(self, buyprice, price):
        profit = price - buyprice
        #if  profit <= 0  or (profit < (self.maxval - price) and self.candles > 2):
        #    print('Buy Price', buyprice, 'Max Value', self.maxval)
        #    self.maxval = 0
        #    return True
        if (self.macdHist <= 0.02 or (self.lasthist - self.macdHist) > 0.01) and self.sar <= self.lastsar:
            #print('Sell Signal: ', self.macdHist - self.lasthist, self.sar - self.lastsar)
            self.Pprofit = self.Pprofit + (100 * (self.maxval - buyprice) / self.maxval)
            #print('pprofit: ', self.Pprofit)
            #print('Max Value', self.maxval, ' Potential Profit :', (100 * (self.maxval - buyprice) / self.maxval), '%\n')
            self.maxval = 0
            return True
        return False