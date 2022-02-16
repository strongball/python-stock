import datetime
import backtrader as bt
import math


class MABadge(bt.Strategy):
    params = (
        ('pfast', 5),
        ('pslow', 20),
        ('buy', 1),
        ('sell', 1),
    )

    def __init__(self, slient=False):
        self.slient = slient
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.order = None
        # self.setsizer(SlowSizeer(0.1))
        self.slow_sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.pfast)

        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    # 交易紀錄
    def log(self, txt, dt=None):
        if self.slient:
            return
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            #主动买卖的订单提交或接受时  - 不触发
            return
        #验证订单是否完成
        #注意: 当现金不足时，券商可以拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: {:.2f}, Size: {}, Cash: {:.2f}'.format(
                        order.executed.price, order.executed.size,
                        self.broker.get_cash()))
            elif order.issell():
                self.log(
                    'SELL EXECUTED, Price: {:.2f}, Size: {}, Cash: {:.2f}'.format(
                        order.executed.price, order.executed.size,
                        self.broker.get_cash()))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(
                'Order Canceled/Margin/Rejected p:{:.2f}, s: {:.2f}, t: {:.2f}, c:{:.2f} '
                .format(order.price, order.size, order.price * order.size,
                        self.broker.get_cash()))
        #重置订单
        self.order = None

    def next(self):
        if self.order:
            return
        # self.log(self.crossover-0)
        if self.fast_sma > self.slow_sma:
            price = self.dataopen[0] * 1.05
            cash = self.broker.get_cash()
            size = math.floor((cash * self.params.buy) / price)
            if size == 0:
                return
            # self.log('BUY CREATE, {:.2f} * {}'.format(self.dataopen[0], size))
            self.order = self.buy(size=size, price=price, exectype=bt.Order.Market)
        else:
            if self.fast_sma < self.slow_sma:
                size = math.floor(self.broker.getposition(self.datas[0]).size * self.params.sell)
                if size == 0:
                    return
                # self.log('CLOSE CREATE, {:.2f} * {}'.format(self.dataopen[0], size))
                # print(self.broker.getposition(self.datas[0]))
                self.order = self.sell(size=size, exectype=bt.Order.Market)


# 計算交易部位
class SlowSizeer(bt.Sizer):
    def __init__(self, percent):
        self.percent = percent

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor((cash * self.percent) / data[1])
        else:
            return math.floor(x)(self.broker.getposition(data) * self.percent)


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    cerebro = bt.Cerebro()
    data = bt.feeds.YahooFinanceData(dataname='TQQQ',
                                     fromdate=datetime.datetime(2018, 1, 1),
                                     todate=datetime.datetime(2019, 12, 31))
    # feed data
    cerebro.adddata(data)
    # add strategy
    cerebro.addstrategy(MABadge, pfast=5, pslow=20, buy=0.5, sell=0.5)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # run backtest
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # # plot diagram
    # plt.figure()
    # cerebro.plot()
    # plt.show()