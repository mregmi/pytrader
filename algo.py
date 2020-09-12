from datetime import datetime, timedelta

import json
import pandas as pd
import numpy as np
import talib as ta
import time

import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num

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
        self.slowcross = False
    
    def CalcAlgos(self, data, idx, price):
        df = data[: idx]
        closep = df['close'].values
        high = df['high'].values
        low = df['low'].values

        #print(closep)
        # Ema 12 26
        self.emaslow = ta.EMA(closep, 9)[-1]
        self.emafast = ta.EMA(closep, 26)[-1]
#       df['EMASlow'] = emaslow
#       df['EMAHigh'] = emafast

        # Stochastic
        slowk, slowd = ta.STOCH(high, low, closep)
        self.slowk = slowk[-1]
        self.slowd = slowd[-1]
        if self.slowk > 80:
            self.slowcross = True

        if self.slowcross == True and self.slowk < 80:
            self.slowcross = False

        # MACD
        macd = ta.MACDEXT(closep, fastperiod=7, slowperiod=13, signalperiod=5, signalmatype=1)
        #macdval = pd.DataFrame(macd[0])
        #macdval = macdval.set_index(data.index)
        #data['MACD_Val'] = macdval.iloc[:,0].values
        #data['MACD_Sig'] = pd.Series(macd[1]).values
        #data['MACD_Hist'] = pd.Series(macd[2]).values
        
        self.lasthist = self.macdHist
        self.macdHist = macd[2][-1] 
        self.macdval = macd[0][-1]
        self.macdavg = macd[1][-1]
        #print(data)
        #print(self.lasthist, self.macdHist)

        #SAR
        self.lastsar = self.sar
        self.sar = ta.SAR(high, low, acceleration=0.02, maximum=0.2)[-1]
        #print(self.lastsar, self.sar)
        if price > self.maxval:
            self.maxval = price
        self.candles = self.candles + 1
        
    def GetBuySignal(self, price):
        if self.macdHist < 0:
            return False
        
        #if price < self.emaslow:
        #    return False

        if self.macdHist <= self.lasthist:
            return False

        #if self.macdval > self.macdavg :
        #    return False

        #if self.sar <= self.lastsar:
        #    return False
        
        #if self.slowk >= 80:
        #    return False

        if self.macdHist > 0.01 and (self.slowk > self.slowd and self.slowk < 80):
            print('Buy Signal: ', self.macdHist - self.lasthist, self.sar, self.lastsar)
            self.candles = 0
            return True
        
        return False

    def GetTotalProfit(self):
        return self.Pprofit
    
    def isMustSell(self, buyprice, price):
        profit = price - buyprice
        percent = (100 * profit) / buyprice
        mprofit = (100 * (self.maxval - buyprice) / self.maxval)
        if percent < -1:
            print('STOP LOSS  Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
            self.maxval = 0
            return True
        if percent < -0.5  and self.candles >= 1:
            #or (profit < (self.maxval - price) 
            print('Y Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
            self.maxval = 0
            return True
        return False
    
    def GetSellSignal(self, buyprice, price):
        profit = price - buyprice
        percent = (100 * profit) / buyprice
        mprofit = (100 * (self.maxval - buyprice) / self.maxval)
        self.Pprofit = self.Pprofit + mprofit
        #if self.slowd > self.slowk:
        #    print('X Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
        #    self.maxval = 0
        #    return True
        if self.slowcross == True:
            self.maxval = 0
            print('SCross Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
            return True
            
        if self.macdHist <= 0:
            print('Z Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
            self.maxval = 0
            return True
        if percent >= 1:
            print('A Buy Price:', buyprice, percent, 'Max Value:', self.maxval, mprofit)
            self.maxval = 0
            return True 
        return self.isMustSell(buyprice, price)
    
    def PlotChart(self, df, ncandles, ticker):
        data = df.iloc[-ncandles:]
        
        # Create figure and set axes for subplots
        fig = plt.figure()
        fig.set_size_inches((20, 16))
        ax_candle = fig.add_axes((0, 0.72, 1, 0.32))
        ax_macd = fig.add_axes((0, 0.48, 1, 0.2), sharex=ax_candle)
        
        # Format x-axis ticks as dates
        ax_candle.xaxis_date()
        # Get nested list of date, open, high, low and close prices
        ohlc = []
        for date, row in data.iterrows():
            closep, highp, lowp, openp = row[:4]
            ohlc.append([date2num(date), openp, highp, lowp, closep])
        #print(data["MACD_Hist"])
        # Plot candlestick chart
        #ax_candle.plot(data.index, data["ma10"], label="MA10")
        #ax_candle.plot(data.index, data["ma30"], label="MA30")
        candlestick_ohlc(ax_candle, ohlc, colorup="g", colordown="r", width=0.6/(24*60))
        ax_candle.legend()
        # Plot MACD
        try:
            ax_macd.plot(data.index, data["MACD_Val"], label="macd")
            ax_macd.bar(data.index, data["MACD_Hist"] * 3, label="hist")
            ax_macd.plot(data.index, data["MACD_Sig"], label="signal")
        except Exception as e:
            print(e)
            print(data)
        ax_macd.legend()
        
        # Save the chart as PNG
        fig.savefig(ticker + ".png", bbox_inches="tight")
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(ticker)
        plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
        plt.show()