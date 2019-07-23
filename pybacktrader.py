from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import alpaca_backtrader_api
import datetime
from pytz import timezone

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.ctime(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        #self.smalow = bt.indicators.MovAv.SMA(self.data, period=13)
        #self.smahigh = bt.indicators.MovAv.SMA(self.data, period=30)
        self.macd = bt.indicators.MACD()

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f MACD %.4f' %
            (self.dataclose[0], self.macd[0]))


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    
    #store = alpaca_backtrader_api.AlpacaStore()

    broker = alpaca_backtrader_api.AlpacaBroker()

    cerebro.setbroker(broker)
    cerebro.broker.cash = 100000.0


    start = datetime.datetime(2019, 7, 8)#.astimezone(timezone('US/Eastern'))
    end = datetime.datetime(2019, 7, 9)#.astimezone(timezone('US/Eastern'))

    print('Starting Portfolio Value: %.2f' % cerebro.broker.cash)
    DataFactory = alpaca_backtrader_api.AlpacaData
    data0 = DataFactory(
        dataname='TQQQ',
        compression=5,
        historical=True,
        fromdate=start,
        todate=end,
        timeframe=bt.TimeFrame.TFrame("Minutes")
        )
    cerebro.adddata(data0)

    cerebro.run(exactbars=5)
    cerebro.plot(iplot=True)
    print('Final Portfolio Value: %.2f' % cerebro.broker.cash)
