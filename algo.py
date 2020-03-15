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
    
    def CalcAlgos(self, df):
        closep = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # Ema 12 26
        self.emaslow = ta.EMA(closep, 12)
        self.emafast = ta.EMA(closep, 26)
#       df['EMASlow'] = emaslow
#       df['EMAHigh'] = emafast

        # MACD
        macd = ta.MACD(closep)
        #print(macd)
#        df['MACD_val'] = macd[0]
#        df['MACD_Sig'] = macd[1]
        self.lasthist = self.macdHist
        self.macdHist = macd[2][-1]
        print(self.lasthist, self.macdHist)

        #SAR
        self.lastsar = self.sar
        self.sar = ta.SAR(high, low, acceleration=0.02, maximum=0.2)[-1]
        print(self.lastsar, self.sar)
        
    def GetBuySignal(self):
        if self.macdHist < 0.02:
            return False

        if self.macdHist - self.lasthist > 0.01 and (self.sar - self.lastsar) > 0.02:
            return True
        
        return False

    def GetSellSignal(self):
        if (self.macdHist <= 0.02 or (self.lasthist - self.macdHist) > 0.01) and self.sar <= self.lastsar:
            logger.info(f'Sell Signal')
            return True
        return False