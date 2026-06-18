from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

QXQS_MAIN_FORMULA = """{QXQS Lab - Main Trend Overlay}
{Research indicator only. Not financial advice.}
{Parameters: P1=5}

WRV:MA(CLOSE,P1),COLORLIGREEN,LINETHICK1;
MID:=(3*CLOSE+LOW+OPEN+HIGH)/6;
DKXV:(20*MID+19*REF(MID,1)+18*REF(MID,2)+17*REF(MID,3)+16*REF(MID,4)+15*REF(MID,5)+14*REF(MID,6)+13*REF(MID,7)+12*REF(MID,8)+11*REF(MID,9)+10*REF(MID,10)+9*REF(MID,11)+8*REF(MID,12)+7*REF(MID,13)+6*REF(MID,14)+5*REF(MID,15)+4*REF(MID,16)+3*REF(MID,17)+2*REF(MID,18)+REF(MID,19))/210,COLORLIGREEN,LINETHICK3;
WRV_UP:IF(WRV>REF(WRV,1),WRV,DRAWNULL),COLORRED,LINETHICK1;
WRV_DN:IF(WRV<REF(WRV,1),WRV,DRAWNULL),COLORLIGREEN,LINETHICK1;
DKXV_UP:IF(DKXV>REF(DKXV,1),DKXV,DRAWNULL),COLORRED,LINETHICK3;
DKXV_DN:IF(DKXV<REF(DKXV,1),DKXV,DRAWNULL),COLORLIGREEN,LINETHICK3;
"""

XDDW_SUB_FORMULA = """{QXQS Lab - XDDW Relative Position Subchart}
{Research indicator only. Not financial advice.}
{Parameters: P1=60, P2=20, P3=5}

A:=20;
B:=80;
FILLRGN(B,100,1,COLORLIGREEN);
FILLRGN(0,A,1,COLORLIRED);
RSV:=(CLOSE-LLV(LOW,P1))/(HHV(HIGH,P1)-LLV(LOW,P1))*100;
K:=SMA(RSV,P2,1);
SLOW:SMA(K,P3,1),COLORBLUE;
FAST:3*K-2*SLOW,COLORBROWN;
LOW_ZONE:A,COLORLIRED;
HIGH_ZONE:B,COLORLIGREEN;
"""

INSTALL_README = """# QXQS Lab Futu/Moomoo Indicator Pack

This folder contains copy-paste formulas for Futu/Moomoo-style custom indicators.

Files:

- `QXQS_Lab_Main_Trend.txt`: main-chart red/green trend overlay.
- `QXQS_Lab_XDDW_Subchart.txt`: sub-chart relative-position indicator.

Important:

- This is not an official Futu/Moomoo plugin.
- This is not a one-click installer.
- This is research software, not financial advice.

Signals should be reviewed after a completed daily candle. Intraday colors can change before the bar closes.
"""


def export_futu_pack(output_dir: str | Path = "outputs/futu-pack") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "QXQS_Lab_Main_Trend.txt": QXQS_MAIN_FORMULA,
        "QXQS_Lab_XDDW_Subchart.txt": XDDW_SUB_FORMULA,
        "README.md": INSTALL_README,
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    zip_path = out.with_suffix(".zip")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for name in files:
            zf.write(out / name, arcname=name)
    return zip_path
