select
    item_code,
    item_name,
    weight,
    series_type,
    series_type_ja,
    year_month,
    year,
    month,
    index_value
from {{ ref('stg_ita_monthly') }}
