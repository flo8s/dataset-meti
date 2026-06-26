"""経済産業省 第３次産業活動指数の取得 + dbt ビルド。

1. ita:  METI 公開 Excel を取得し縦持ち CSV へ整形（季調・原の月次）
2. dbt:  dbt ビルド
"""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

from ita import download_and_parse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipelines")

FDL_DIR = Path(".fdl")
CSV_PATH = FDL_DIR / "meti_ita_monthly.csv"


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["run"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    FDL_DIR.mkdir(exist_ok=True)

    logger.info("1/2: ita (第３次産業活動指数 月次)")
    rows = download_and_parse(CSV_PATH)
    logger.info(f"  meti_ita_monthly.csv: {rows} rows")

    logger.info("2/2: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
