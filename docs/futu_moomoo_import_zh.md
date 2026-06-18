# 富途/牛牛指标导入教程

QXQS Lab 提供一套富途/牛牛风格的自定义指标公式包，包含主图红绿趋势线和副图相对点位。

这不是富途官方插件，也不是一键安装器。它是一个可复制粘贴到自定义指标里的公式包。

## 生成公式包

```bash
qxqs export-futu
```

生成文件：

```text
outputs/futu-pack/QXQS_Lab_Main_Trend.txt
outputs/futu-pack/QXQS_Lab_XDDW_Subchart.txt
outputs/futu-pack.zip
```

## 安装主图指标

1. 打开富途/牛牛桌面端。
2. 打开任意标的的日 K 线。
3. 右键 K 线图，进入指标管理或自定义指标。
4. 新建主图指标。
5. 复制 `QXQS_Lab_Main_Trend.txt` 全部内容。
6. 设置参数 `P1 = 5`。
7. 保存为 `QXQS Lab Main`。

## 安装副图指标

1. 新建副图指标。
2. 复制 `QXQS_Lab_XDDW_Subchart.txt` 全部内容。
3. 设置参数 `P1 = 60`，`P2 = 20`，`P3 = 5`。
4. 保存为 `QXQS Lab XDDW`。

## 手机端说明

部分富途/牛牛客户端可能支持桌面端自定义指标同步到手机端，但取决于客户端版本和账户同步能力。

如果手机端无法显示自定义指标，建议使用 QXQS Lab 的移动端截图页：

```bash
pip install -e ".[web]"
qxqs web
```

打开 `http://localhost:8501`，输入标的，生成 4:5 小红书截图。

## 复盘边界

指标只是研究工具，不是买卖指令。尽量用日线收盘后的信号，不建议盘中追颜色变化。
