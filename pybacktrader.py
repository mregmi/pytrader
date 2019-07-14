from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import datetime

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(100000.0)

    start = datetime.datetime(2019, 7, 8)
    end = datetime.datetime(2019, 7, 10)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    data = bt.feeds.YahooFinanceData(dataname="AAPL", fromdate=start, todate=end)
    cerebro.adddata(data)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
