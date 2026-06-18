# QXQS Lab Futu/Moomoo Indicator Pack

This folder contains copy-paste formulas for Futu/Moomoo-style custom indicators.

Files:

- `QXQS_Lab_Main_Trend.txt`: main-chart red/green trend overlay.
- `QXQS_Lab_XDDW_Subchart.txt`: sub-chart relative-position indicator.

Important:

- This is not an official Futu/Moomoo plugin.
- This is not a one-click installer.
- This is research software, not financial advice.
- If your client supports `.ftindex` import, you can manually create/export that file after adding the indicators.

Suggested install flow:

1. Open Futu/Moomoo desktop.
2. Open any symbol's daily K-line chart.
3. Right-click the chart and open indicator management.
4. Create a new main-chart indicator.
5. Copy `QXQS_Lab_Main_Trend.txt` into the formula editor.
6. Set parameter `P1 = 5`.
7. Save it as `QXQS Lab Main`.
8. Create a new sub-chart indicator.
9. Copy `QXQS_Lab_XDDW_Subchart.txt` into the formula editor.
10. Set parameters `P1 = 60`, `P2 = 20`, `P3 = 5`.
11. Save it as `QXQS Lab XDDW`.

Signals should be reviewed after a completed daily candle. Intraday colors can change before the bar closes.
