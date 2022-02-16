# 使用backtrader 測試演算法
# %%
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import backtrader as bt
import backtrader.feeds as feeds
import yfinance as yf

from MAcrossover import MAcrossover
# 從Yahoo Finance取得資料
data = feeds.PandasData(
    dataname=yf.download('QQQ', '2021-07-01', '2022-02-10', auto_adjust=True))


def show():
    # %%
    cerebro = bt.Cerebro()
    # feed data
    cerebro.adddata(data)
    # add strategy
    cerebro.addstrategy(MAcrossover, log=True, pfast=5, pslow=20)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # run backtest
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # plot diagram
    plt.figure()
    cerebro.plot()
    plt.show()


# %%
show()
