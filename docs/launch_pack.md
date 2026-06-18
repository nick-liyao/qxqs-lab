# Launch Pack Workflow

`qxqs launch-pack` generates the first batch of mobile-first charts and captions for Xiaohongshu, Douyin, X, and GitHub launch posts.

```bash
qxqs launch-pack
```

Default symbols:

```text
QQQ NVDA TSLA SPY MSTR GDX KWEB
```

Outputs:

- `outputs/launch/charts/*.png`: 4:5 chart images for mobile feeds.
- `outputs/launch/captions/*.md`: Chinese captions with a GitHub Star call to action.
- `outputs/launch/manifest.json`: machine-readable summary for later automation.
- `outputs/launch/README.md`: posting checklist for the current batch.

Custom batch:

```bash
qxqs launch-pack --symbols QQQ NVDA TSLA --range 1y --output-dir outputs/launch-ai
```

Discovery batch:

```bash
qxqs launch-pack --discover --limit 7
```

Discovery scans a hot AI, semiconductor, crypto-adjacent, and ETF universe, ranks symbols by current signal, recent signal date, and simple backtest readability, then generates assets for the selected symbols. It also writes:

- `outputs/launch/discovery.md`
- `outputs/launch/discovery.json`

## Posting Loop

1. Pick one chart from `outputs/launch/charts`.
2. Open the matching caption from `outputs/launch/captions`.
3. Add one human observation from the current market context.
4. Publish with the GitHub CTA: `GitHub 搜 qxqs-lab，觉得有用可以点 Star。`
5. Reply to comments with the repo link and ask what symbols users want next.

Boundary: QXQS Lab is a research and education tool. Do not write guaranteed-profit, trade-instruction, or account-performance claims.
