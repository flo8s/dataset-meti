{# 経済産業省 第３次産業活動指数（2020年基準）月次データの生データ。
   main.py が METI 公開 Excel を取得・整形して .fdl/meti_ita_monthly.csv に保存する。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.fdl/meti_ita_monthly.csv',
    header=true,
    columns={
        'item_code': 'VARCHAR',
        'item_name': 'VARCHAR',
        'weight': 'DOUBLE',
        'series_type': 'VARCHAR',
        'series_type_ja': 'VARCHAR',
        'year_month': 'VARCHAR',
        'index_value': 'DOUBLE'
    }
)
