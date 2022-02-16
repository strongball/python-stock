# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import math
from MABadge import MABadge

start = 2018
period = 2
print("From: {}, To: {}".format(start, start - 1 + period))
# 從Yahoo Finance取得資料
data = btfeeds.YahooFinanceData(dataname='TQQQ',
                                fromdate=datetime.datetime(start, 1, 1),
                                todate=datetime.datetime(
                                    start + period, 12, 31))

# %%
# sma cross strategy


# %%
def train():
    # 初始化cerebro
    cerebro = bt.Cerebro(optreturn=False)
    # feed data
    cerebro.adddata(data)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.optstrategy(
        MABadge,
        # buy=[x / 10 for x in range(2, 11, 4)],
        # sell=0,
        # sell=[0, 0.1, 1],
        pfast=[3, 5, 10],
        pslow=[10, 20, 50])

    optimized_runs = cerebro.run()
    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() / 10000, 2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append({
                'buy': strategy.params.buy,
                'sell': strategy.params.sell,
                'pfast': strategy.params.pfast,
                'pslow': strategy.params.pslow,
                'p': PnL,
                'sharpe': sharpe['sharperatio'],
            })

    sort_by_sharpe = sorted(final_results_list,
                            key=lambda x: x['p'],
                            reverse=True)
    for line in sort_by_sharpe[:20]:
        print(line)


def show():
    # %%
    cerebro = bt.Cerebro()
    # feed data
    cerebro.adddata(data)
    # add strategy
    cerebro.addstrategy(MABadge, buy=1, sell=1, pfast=5, pslow=20)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # run backtest
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # plot diagram
    plt.figure()
    cerebro.plot()
    plt.show()


# %%
# train()
show()
