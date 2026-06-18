from __future__ import annotations

SIGNAL_ZH = {
    "BBB": {"title": "急跌新低", "tone": "机会观察", "explain": "价格处在急跌和新低附近，偏离中期趋势线较深，适合放入重点观察池。", "action": "不代表立刻买入，建议等日线收盘后结合趋势线修复再判断。"},
    "B": {"title": "回踩建仓", "tone": "机会观察", "explain": "价格回到趋势线附近，短期趋势和相对位置开始修复，是低频复盘里较常见的观察点。", "action": "适合记录为复盘候选，不建议盘中追信号。"},
    "HOT": {"title": "高位过热", "tone": "风险提醒", "explain": "价格相对趋势线偏离较大，XDDW 处于高位区域，短线有回落或震荡需求。", "action": "适合检查仓位和止盈计划，不是自动卖出指令。"},
    "SSS": {"title": "破位强风险", "tone": "风险提醒", "explain": "趋势线转弱并出现结构破位，模型认为风险级别较高。", "action": "适合优先控制风险，等待下一次趋势修复。"},
    "SS": {"title": "中风险", "tone": "风险提醒", "explain": "趋势出现转弱或反弹失败迹象，但不一定已经形成强破位。", "action": "适合降低激进预期，继续观察后续日线确认。"},
    "S": {"title": "轻风险", "tone": "轻提醒", "explain": "短期反弹失败或趋势开始转弱，是早期风险提醒。", "action": "适合复盘，不建议单独作为交易依据。"},
    "none": {"title": "无新信号", "tone": "等待确认", "explain": "当前没有新的分档信号，更多是观察趋势线和相对位置的状态。", "action": "等待更明确的日线信号。"},
}


def zh_signal_text(label: object) -> dict[str, str]:
    return SIGNAL_ZH.get(str(label or "none"), SIGNAL_ZH["none"])


def social_caption(symbol: str, summary: dict[str, object], backtest_summary: object) -> str:
    signal = zh_signal_text(summary.get("signal"))
    return (
        f"{symbol} 今日 QXQS Lab 复盘：{signal['title']} / {signal['tone']}。\n"
        f"收盘价：{summary.get('close')}；DKXV：{summary.get('DKXV_color')}；XDDW：{summary.get('FAST2')} / {summary.get('SLOW2')}。\n"
        f"解读：{signal['explain']}\n"
        f"回测摘要：策略 {getattr(backtest_summary, 'total_return_pct', 'NA')}%，买入持有 {getattr(backtest_summary, 'buy_hold_return_pct', 'NA')}%，最大回撤 {getattr(backtest_summary, 'max_drawdown_pct', 'NA')}%。\n"
        "不是荐股，不是买卖建议，只展示一个开源低频复盘工具。\n"
        "GitHub 搜 qxqs-lab，觉得有用可以点 Star。"
    )
