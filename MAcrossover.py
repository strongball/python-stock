import datetime
import backtrader as bt
import math


class MAcrossover(bt.Strategy):
    params = (
        ('log', False),
        ('pfast', 5),
        ('pslow', 20),
    )

    # 交易紀錄
    def log(self, txt, dt=None):
        if self.params.log:
            dt = dt or self.datas[0].datetime.date(0)
            print('[%s] %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.first = True
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.order = None
        self.setsizer(sizer())
        self.slow_sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.pfast)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            #主动买卖的订单提交或接受时  - 不触发
            return
        #验证订单是否完成
        #注意: 当现金不足时，券商可以拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        #重置订单
        self.order = None

    def next(self):
        # 检测是否有未完成订单
        if self.order:
            return
            
        if self.fast_sma > self.slow_sma:
            if self.position.size < 0:
                self.close()
            elif self.position.size == 0:
                self.log('Long CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        #如果SMA快线跌破SMA慢线
        else:
            if self.position.size > 0:
                self.close()
            # elif self.position.size == 0:
            #     self.log('Short CREATE, %.2f' % self.dataclose[0])
            #     self.order = self.sell()

# 計算交易部位
class sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            if self.broker.getposition(data).size < 0:
                return self.broker.getposition(data)
            return math.floor((cash * 0.95) / data[1])
        else:
            if self.broker.getposition(data).size > 0:
                return self.broker.getposition(data)
            return math.floor((cash * 0.95) / data[1])
