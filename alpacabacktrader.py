import os
import argparse
import pandas as pd
import alpaca_trade_api as ata
import datetime as dt
from pytz import timezone

def main(symbol,date,start,ticks,cond):
    full_date = date+" "+start
    st = dt.datetime.strptime(full_date, '%d-%m-%Y %H:%M:%S')
    st = timezone('US/Eastern').localize(st)
    #st = int(st.timestamp())*1000
    dateto = st + dt.timedelta(days=1)
    trades = ata.REST().polygon.historic_agg_v2(symbol, 1, 'day', _from=st, to=dateto)
    trades.df.reset_index(level=0, inplace=True)
    print("starting trades")
    print(trades)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, default='SPY', help='symbol you want to get data for')
    parser.add_argument('--date', type=str, default='2019-09-19', help='date you want to get data for')
    parser.add_argument('--start', type=str, default='09:30:00', help='start time you want to get data for')
    parser.add_argument('--ticks', type=int, default=10000, help='number of ticks to retrieve')
    parser.add_argument('--conditions', action='store_true', default=False)
    args = parser.parse_args()
    main(args.symbol,args.date,args.start,args.ticks,args.conditions)
    
   # time.strptime("2019–12", "%Y-%m")