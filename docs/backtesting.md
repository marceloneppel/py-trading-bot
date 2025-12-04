# Backtesting
The bot heavily relies on vectorbt, which is designed to perform backtesting. 

To backtest your strategy with historical data (see [download data](https://github.com/psemdel/py-trading-bot/blob/main/docs/download_data.md)), use the Jupyter notebooks:

- strat.ipynb to backtest strategy for one stock
- presel.ipynb to backtest strategy for several stocks
- presel_classic.ipynb to backtest classical portfolio optimization strategy from libraries like PortfolioOptimizer and universal-portfolios which integrated in vbt

Advantage of backtesting from downloaded files:

1. You don't have to download the data again and again
2. They don't change. It makes comparison between strategies easier

# Scan
Additionally, you can backtest with recent prices, for instance last 3 years, using the scan function on the home page. 



