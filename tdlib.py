from tdameritrade import TDClient
from datetime import datetime, timedelta

import json
import requests
import pandas as pd
import numpy as np
import talib as ta
import time

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

    def doClosingSell(self, price, dt):
        if self.bought is True:
            self.bpower += self.nstocks * price
            self.nstocks = 0
            self.bought = False
            print(dt, 'SELL, ', self.buyprice, price, 100 * (price - self.buyprice) / price)
        print(dt, " P/L :", 100 * (self.bpower - self.capital) / self.bpower, end='\n\n')
        self.pl += self.bpower - self.capital
        self.newday = False
        self.bpower = self.capital

    def doSell(self, price, dt):
        self.bpower += self.nstocks * price
        self.nstocks = 0
        self.bought = False
        print(dt, 'SELL, ', self.buyprice, price, 100 * (price - self.buyprice) / price)

    def doBuy(self, price, dt):
        self.nstocks = self.bpower / price
        self.buyprice = price
        self.bpower -= self.nstocks * price
        self.bought = True
        print(dt, 'BUY ', self.nstocks, price)

    def tradelogic(self, df, dt):
        self.add_indicators(df)
        lastdf = df.tail(1)

        macdHist = lastdf.iloc[0]['MACD_hist']#getattr(lastdf, 'MACD_hist')
        price = lastdf.iloc[0]['close']#getattr(lastdf, 'close')
        sar = lastdf.iloc[0]['SAR']

        #if np.isnan(macdHist):
        #    return
        #print('H HU HU', price, macdHist, dt)

        if  dt >= datetime(dt.year, dt.month, dt.day, 13, 00):
            self.doClosingSell(price, dt)
            return
        if macdHist > 0.01 and macdHist > self.lasthist and (sar - self.lastsar) > 0.02 and self.bought is False:
            self.doBuy(price, dt)
        elif (macdHist <= 0 or macdHist < self.lasthist) and sar <= self.lastsar and self.bought is True:
            self.doSell(price, dt)

        self.lastsar = sar
        self.lasthist = macdHist

    def backtradelogic(self, df):
        self.add_indicators(df)
        for row in df.itertuples():
            macdHist = getattr(row, 'MACD_hist')
            price = getattr(row, 'close')
            sar = getattr(row, 'SAR')

            if np.isnan(macdHist):
                continue

            dt = row[0].to_pydatetime()
            if  dt >= datetime(dt.year, dt.month, dt.day, 13, 00) and self.newday is True:
                self.doClosingSell(price, dt)
                continue

            if dt < datetime(dt.year, dt.month, dt.day, 6, 30) or dt > datetime(dt.year, dt.month, dt.day, 13, 00):
                continue

            self.newday = True
            if macdHist > 0.01 and macdHist > self.lasthist and (sar - self.lastsar) > 0.02 and self.bought is False:
                self.doBuy(price, dt)
            elif (macdHist <= 0 or macdHist < self.lasthist) and sar <= self.lastsar and self.bought is True:
                self.doSell(price, dt)

            self.lastsar = sar
            self.lasthist = macdHist

        if self.bought is True:
            self.doSell(price, dt)
