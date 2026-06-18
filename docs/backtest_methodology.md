# Backtest Methodology

QXQS Lab uses a simple next-bar research backtest.

Signals are calculated on the current completed bar. Trades are simulated on the next bar's open. This avoids trading on information that would not have been available at signal time.
