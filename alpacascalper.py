import alpaca_trade_api as alpaca
import asyncio
import pandas as pd
import sys
import time
import datetime

import logging
from algo import TraderAlgo

logger = logging.getLogger()


class ScalpAlgo:

    def __init__(self, api, symbol, lot):
        self._api = api
        self._symbol = symbol
        self._lot = lot
        self.qty = 0
        self.once = True
        self._bars = []
        self._l = logger.getChild(self._symbol)

        now = pd.Timestamp.now(tz='America/New_York').floor('1min')
        market_open = now.replace(hour=9, minute=30)
        today = now.strftime('%Y-%m-%d')
        tomorrow = (now + pd.Timedelta('1day')).strftime('%Y-%m-%d')
        data = api.polygon.historic_agg_v2(
            symbol, 1, 'minute', today, tomorrow, unadjusted=False).df
        bars = data[market_open:]
        self._bars = bars

        self._init_state()
        self.algo = TraderAlgo(symbol, lot)

    def _init_state(self):
        symbol = self._symbol
        order = [o for o in self._api.list_orders() if o.symbol == symbol]
        position = [p for p in self._api.list_positions()
                    if p.symbol == symbol]
        self._order = order[0] if len(order) > 0 else None
        self._position = position[0] if len(position) > 0 else None
        if self._position is not None:
            self._state = 'TO_SELL'
        else:
            self._state = 'TO_BUY'

    def _now(self):
        return pd.Timestamp.now(tz='America/New_York')

    def _outofmarket(self):
        return self._now().time() >= pd.Timestamp('15:55').time()

    def checkup(self, position):
        # self._l.info('periodic task')

        now = self._now()
#        order = self._order
#        if (order is not None and
#            order.side == 'buy' and now -
#                pd.Timestamp(order.submitted_at, tz='America/New_York') > pd.Timedelta('2 min')):
#            last_price = self._api.polygon.last_trade(self._symbol).price
#            self._l.info(
#                f'canceling missed buy order {order.id} at {order.limit_price} '
#                f'(current price = {last_price})')
#            self._cancel_order()

#        if self._position is not None and self._outofmarket():
#            self._submit_sell(bailout=True)

    def _cancel_order(self):
        if self._order is not None:
            self._api.cancel_order(self._order.id)

    def on_bar(self, bar):
        self._bars = self._bars.append(pd.DataFrame({
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume,
        }, index=[bar.start]))

        self._l.info(
            f'received bar start = {bar.start}, close = {bar.close}, len(bars) = {len(self._bars)}')
        if len(self._bars) < 26:
            return
        if self._outofmarket():
            return
        if self.once == True:
            self.once = False
            return
        
        self.algo.CalcAlgos(self._bars)
        if self._state == 'TO_BUY':
            signal = self.algo.GetBuySignal()
            if signal:
                self._submit_buy()
        if self._state == 'TO_SELL':
            signal = self.algo.GetSellSignal()
            if signal:
                self._submit_sell()
        self.once = False

    def on_order_update(self, event, order):
        self._l.info(f'order update: {event} = {order}')

    def _submit_buy(self):
        for i in range(0,4):
            try:
                trade = self._api.polygon.last_trade(self._symbol)
                amount = int(self._lot / trade.price)
                order = self._api.submit_order(
                    symbol=self._symbol,
                    side='buy',
                    type='market',
                    qty=amount,
                    time_in_force='day',
#                   limit_price=trade.price,
                )
                break
            except Exception as e:
                self._l.info(e)
                self._l.info(f'Retrying again after 2 seconds')
                time.sleep(2) 
                #self._transition('TO_BUY')
        self._order = order
        self.qty = amount
        self._l.info(f'submitted buy {order}')
        self._transition('TO_SELL')

    def _submit_sell(self, bailout=False):
        params = dict(
            symbol=self._symbol,
            side='sell',
            qty=self.qty,
            time_in_force='day',
            type='market'
        )
#        if bailout:
#            params['type'] = 'market'
#        else:
#            current_price = float(
#                self._api.polygon.last_trade(
#                    self._symbol).price)
#            cost_basis = float(self._position.avg_entry_price)
#            limit_price = max(cost_basis + 0.01, current_price)
#            params.update(dict(
#                type='limit',
#                limit_price=limit_price,
#            ))
        for i in range(0,4):
            try:
                order = self._api.submit_order(**params)
                break
            except Exception as e:
                self._l.error(e)
                self._l.info(f'Retrying again after 2 seconds')
                time.sleep(2) 

        self._order = order
        self._l.info(f'submitted sell {order}')
        self._transition('TO_BUY')

    def _transition(self, new_state):
        self._l.info(f'transition from {self._state} to {new_state}')
        self._state = new_state


def main(args):
    api = alpaca.REST()
    stream = alpaca.StreamConn()

    fleet = {}
    symbols = args.symbols
    for symbol in symbols:
        algo = ScalpAlgo(api, symbol, lot=args.lot)
        fleet[symbol] = algo

    @stream.on(r'^AM')
    async def on_bars(conn, channel, data):
        if data.symbol in fleet:
            fleet[data.symbol].on_bar(data)

    @stream.on(r'trade_updates')
    async def on_trade_updates(conn, channel, data):
        logger.info(f'trade_updates {data}')
        symbol = data.order['symbol']
        if symbol in fleet:
            fleet[symbol].on_order_update(data.event, data.order)

    async def periodic():
        print(datetime.datetime.now())
        while True:
            if not api.get_clock().is_open:
                logger.info('exit as market is not open')
                #sys.exit(0)
            await asyncio.sleep(30)
            try:
                positions = api.list_positions()
            except Exception as e:
                logger.info(e)
                continue
            for symbol, algo in fleet.items():
                pos = [p for p in positions if p.symbol == symbol]
                algo.checkup(pos[0] if len(pos) > 0 else None)
    channels = ['trade_updates'] + [
        'AM.' + symbol for symbol in symbols
    ]

    loop = stream.loop
    loop.run_until_complete(asyncio.gather(
        stream.subscribe(channels),
        periodic(),
    ))
    loop.close()


if __name__ == '__main__':
    import argparse

    fmt = '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    fh = logging.FileHandler('console.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt))
    logger.addHandler(fh)

    parser = argparse.ArgumentParser()
    parser.add_argument('symbols', nargs='+')
    parser.add_argument('--lot', type=float, default=2000)

    main(parser.parse_args())
    