{# 年月（YYYYMM）から年・月を切り出して付与する。 #}

select
    item_code,
    item_name,
    weight,
    series_type,
    series_type_ja,
    year_month,
    cast(substr(year_month, 1, 4) as integer) as year,
    cast(substr(year_month, 5, 2) as integer) as month,
    index_value
from {{ ref('raw_ita_monthly') }}
