from tdameritrade import TDClient
from datetime import datetime

import json
import requests
import pandas as pd
import numpy as np
import talib as ta
#from talib.abstract import *

class TDTrader:
    def __init__(self):
        json_file = open('td_auth.json')
        jsondata = json.load(json_file)
        self.access_token = jsondata['access_token']
        self.refresh_token = jsondata['refresh_token']
        self.client = TDClient(self.access_token)
        self.capital = 100000
        self.bpower = self.capital
        self.pl = 0
        self.bought = False
        self.buyprice = 0
        self.nstocks = 0
        self.lastsar = 0
        self.lasthist = 0
        self.newday = True

    def do_refresh_token(self):
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        data = { 'grant_type': 'refresh_token', 'access_type': 'offline',
            'refresh_token': self.refresh_token,
            'client_id': 'MTD405', 'redirect_uri': 'http://localhost:8080'}
        authReply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
        jsondata = json.loads(authReply.text)
        if 'access_token' not in jsondata:
            print(jsondata)
            raise ValueError("Received invalid auth tocken")
        self.access_token = jsondata['access_token']
        self.refresh_token = jsondata['refresh_token']
        outfile = open('td_auth.json', 'w')
        outfile.write(authReply.text)
        outfile.close()
        self.client = TDClient(self.access_token)

    def get_account(self):
        try:
            acc = self.client.accounts()
        except Exception as e:
            print(e)
            print('Refreshing access token. it will overwrite auth json file')
            self.do_refresh_token()
            acc = self.client.accounts()
        return acc
    
    def get_quote(self, ticker):
        try:
            acc = self.client.quoteDF(ticker)
        except Exception as e:
            print(e)
            print('Refreshing access token. it will overwrite auth json file')
            self.do_refresh_token()
            acc = self.client.quoteDF(ticker)
        return acc
    
    def get_history(self, ticker):
        try:
            acc = self.client.historyDF(ticker)
        except Exception as e:
            print(e)
            print('Refreshing access token. it will overwrite auth json file')
            self.do_refresh_token()
            acc = self.client.historyDF(ticker)
        return acc

    def add_indicators(self, df):
        closep = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # Ema 12 26
        emaslow = ta.EMA(closep, 12)
        emafast = ta.EMA(closep, 26)
        df['EMASlow'] = emaslow
        df['EMAHigh'] = emafast

        # MACD
        macd = ta.MACD(closep)
        df['MACD_val'] = macd[0]
        df['MACD_Sig'] = macd[1]
        df['MACD_hist'] = macd[2]

        #SAR
        sar = ta.SAR(high, low, acceleration=0.02, maximum=0.2)
        df['SAR'] = sar

    #def doSell(self, price)
    def backtradelogic(self, df):
        self.add_indicators(df)
        for row in df.itertuples():
            macdHist = getattr(row, 'MACD_hist')
            price = getattr(row, 'close')
            sar = getattr(row, 'SAR')

            if np.isnan(macdHist):
                continue

            dt = row[0].to_pydatetime()
            if  dt >= datetime(dt.year, dt.month, dt.day, 20, 00) and self.newday is True:
                if self.bought is True:
                    self.bpower += self.nstocks * price
                    self.nstocks = 0
                    self.bought = False
                    print(row[0], 'SELL, ', self.buyprice, price, 100 * (price - self.buyprice) / price)
                print(dt, " P/L :", 100 * (self.bpower - self.capital) / self.bpower, end='\n\n')
                self.pl += self.bpower - self.capital
                self.newday = False
                self.bpower = self.capital
                continue
            if dt < datetime(dt.year, dt.month, dt.day, 13, 30) or dt > datetime(dt.year, dt.month, dt.day, 20, 00):
                #print(dt.ctime())
                continue
            #print(dt.month, dt.day, dt.hour)
            self.newday = True
            if macdHist > 0.01 and macdHist > self.lasthist and (sar - self.lastsar) > 0.02 and self.bought is False:
                self.nstocks = self.bpower / price
                self.buyprice = price
                self.bpower -= self.nstocks * price
                self.bought = True
                print(row[0], 'BUY ', self.nstocks, price, self.lastsar, sar, macdHist, self.lasthist)
            elif (macdHist <= 0 or macdHist < self.lasthist) and sar <= self.lastsar and self.bought is True:
                self.bpower += self.nstocks * price
                self.nstocks = 0
                self.bought = False
                print(row[0], 'SELL, ', self.buyprice, price, 100 * (price - self.buyprice) / price)
                
            self.lastsar = sar
            self.lasthist = macdHist

        if self.bought is True:
            self.bpower += self.nstocks * price
            self.nstocks = 0
            self.bought = False
            print(row[0], 'SELL, ', self.buyprice, price, 100 * (price - self.buyprice) / price)

if __name__ == '__main__':
    obj = TDTrader()
    accinfo = obj.get_account()

    quote = obj.get_history('JNUG')
    mask = (quote['datetime'] > '2019-07-10 08:00:00') & (quote['datetime'] <= '2019-07-22 23:00:00')
    quote = quote.loc[mask]
    quote.set_index('datetime', inplace=True)

    quote = quote.resample('5T').agg(
        {'close':'last', 'high':np.max, 'low':np.min, 'open':'first', 'volume':np.sum})
    quote = quote.dropna()
    obj.backtradelogic(quote)
    print("P/L : ", 100 * obj.pl / obj.capital)

