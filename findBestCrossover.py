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
    dataname=yf.download('QQQ', '2016-01-01', '2020-12-31', auto_adjust=True))


# %%
def train():
    # 初始化cerebro
    cerebro = bt.Cerebro(optreturn=False)
    # feed data
    cerebro.adddata(data)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.optstrategy(MAcrossover, pfast=[3, 5, 7], pslow=[10, 15, 20, 50])

    optimized_runs = cerebro.run()
    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() / 10000, 2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append({
                "pfast": strategy.params.pfast,
                "pslow": strategy.params.pslow,
                "PnL": PnL,
                "sharperatio": sharpe["sharperatio"]
            })
    sort_by_sharpe = sorted(final_results_list,
                            key=lambda x: x["PnL"],
                            reverse=True)
    for line in sort_by_sharpe:
        print(line)


# %%
train()
