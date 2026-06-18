from zipfile import ZipFile

from qxqs.integrations.futu import export_futu_pack


def test_export_futu_pack(tmp_path):
    zip_path = export_futu_pack(tmp_path / "futu-pack")
    assert zip_path.exists()
    with ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "QXQS_Lab_Main_Trend.txt" in names
    assert "QXQS_Lab_XDDW_Subchart.txt" in names
    assert "README.md" in names
