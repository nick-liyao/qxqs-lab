# Futu/Moomoo Indicator Import

QXQS Lab provides a Futu/Moomoo-style indicator pack for users who want to view the trend overlay and XDDW subchart inside their charting workflow.

This is not an official Futu/Moomoo plugin and not a one-click installer. It is a copy-paste indicator formula package.

## Export the Pack

```bash
qxqs export-futu
```

Output:

```text
outputs/futu-pack/
  QXQS_Lab_Main_Trend.txt
  QXQS_Lab_XDDW_Subchart.txt
  README.md
outputs/futu-pack.zip
```

## Main Chart: QXQS Lab Main

Use `QXQS_Lab_Main_Trend.txt` as a main-chart indicator. Suggested parameter: `P1 = 5`.

## Subchart: QXQS Lab XDDW

Use `QXQS_Lab_XDDW_Subchart.txt` as a sub-chart indicator. Suggested parameters: `P1 = 60`, `P2 = 20`, `P3 = 5`.

## Suggested Manual Install Flow

1. Open Futu/Moomoo desktop.
2. Open any symbol's daily K-line chart.
3. Right-click the chart and open indicator management.
4. Create a new main-chart indicator.
5. Copy `QXQS_Lab_Main_Trend.txt` into the formula editor.
6. Save it as `QXQS Lab Main`.
7. Create a new sub-chart indicator.
8. Copy `QXQS_Lab_XDDW_Subchart.txt` into the formula editor.
9. Save it as `QXQS Lab XDDW`.

## Mobile Usage

If your Futu/Moomoo mobile app can sync desktop custom indicators, the imported indicators may become available on mobile after account sync.

If not, use the QXQS Lab mobile-friendly chart export:

```bash
qxqs chart examples/sample_data/sample_ohlcv.csv --symbol SAMPLE --profile xhs --output outputs/charts/sample-xhs.png
```

The `xhs` profile is designed for 4:5 vertical social-media screenshots.

## Research Boundary

Signals should be reviewed after a completed daily candle. Intraday colors can change before the bar closes.

This project is for research and education only. It is not financial advice.
