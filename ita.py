"""経済産業省 第３次産業活動指数（2020年基準）月次データの取得・整形。

経済産業省 経済解析室が公開する Excel を取得し、ワイド形式（業種×月）の
指数表を縦持ち（業種×月の1行=1指数値）へ展開して CSV に保存する。

季節調整済指数と原指数の2系列を series_type で区別して1つの CSV にまとめる。
"""

import csv
import re
from pathlib import Path

import openpyxl
from curl_cffi import requests

# 経済産業省 第３次産業（サービス産業）活動指数 統計表（2020年基準・月次）
BASE_URL = "https://www.meti.go.jp/statistics/tyo/sanzi/result/excel/"

# (ファイル名, 系列コード, 系列名)
SERIES = [
    ("b2020_ksmj.xlsx", "seasonally_adjusted", "季節調整済指数"),
    ("b2020_komj.xlsx", "original", "原指数"),
]

# 月列のヘッダ（YYYYMM）判定
_YEAR_MONTH = re.compile(r"^(20\d{2})(0[1-9]|1[0-2])$")

OUTPUT_COLUMNS = [
    "item_code",
    "item_name",
    "weight",
    "series_type",
    "series_type_ja",
    "year_month",
    "index_value",
]


def _fetch(filename: str, dest: Path) -> None:
    """METI の Excel を取得して保存する。

    METI のサーバはブラウザ以外の TLS クライアントを遮断するため、
    curl_cffi の impersonate でブラウザの TLS を模倣して取得する。
    """
    resp = requests.get(BASE_URL + filename, impersonate="chrome", timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


def _parse(path: Path, series_type: str, series_type_ja: str) -> list[tuple]:
    """ワイド形式の Excel を縦持ちの行リストへ展開する。

    シート 'ITA' は次の構成:
      - ヘッダ行: 品目番号 | 品目名称 | ウエイト | 201801 | 201802 | ...
      - 以降の各行: 業種ごとの指数（各月列に指数値）
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["ITA"]
    rows = list(ws.iter_rows(values_only=True))

    header_idx = next(
        i for i, r in enumerate(rows) if r and str(r[0]).strip() == "品目番号"
    )
    header = rows[header_idx]

    # 月列のインデックス -> YYYYMM
    month_cols: dict[int, str] = {}
    for ci, val in enumerate(header):
        if val is None:
            continue
        s = str(val).strip()
        s = s.split(".")[0] if s.replace(".", "").isdigit() else s
        if _YEAR_MONTH.match(s):
            month_cols[ci] = s

    out: list[tuple] = []
    for r in rows[header_idx + 1 :]:
        if not r or r[0] is None:
            continue
        item_code = str(r[0]).strip()
        item_name = str(r[1]).strip() if r[1] is not None else None
        weight = r[2]
        for ci, year_month in month_cols.items():
            value = r[ci] if ci < len(r) else None
            # 数値セルのみ採用（空欄・記号セルは欠測としてスキップ）
            if not isinstance(value, (int, float)):
                continue
            out.append(
                (
                    item_code,
                    item_name,
                    weight,
                    series_type,
                    series_type_ja,
                    year_month,
                    value,
                )
            )
    return out


def download_and_parse(csv_path: Path, work_dir: Path | None = None) -> int:
    """全系列を取得・整形して 1 つの CSV に書き出し、行数を返す。"""
    work_dir = Path(work_dir) if work_dir else csv_path.parent
    work_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[tuple] = []
    for filename, series_type, series_type_ja in SERIES:
        xlsx_path = work_dir / filename
        _fetch(filename, xlsx_path)
        all_rows.extend(_parse(xlsx_path, series_type, series_type_ja))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(all_rows)

    return len(all_rows)
