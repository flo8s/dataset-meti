## データ出典

[経済産業省 経済解析室](https://www.meti.go.jp/statistics/tyo/sanzi/)が公表する
第３次産業活動指数（2020年基準）です。サービス産業の生産活動を業種別・月次の指数（2020年=100）で示します。
季節調整済指数と原指数の2系列を収録しています。

## テーブル: tertiary_industry_activity_index

業種（品目）×月×系列種別を1レコードとする月次指数です。2018年1月以降を収録します。

- item_code: 品目番号（VARCHAR、例: K1D000000I = 第３次産業総合）
- item_name: 品目名称（VARCHAR、業種名）
- weight: ウエイト（DOUBLE、2020年基準の付加価値額ウエイト。第３次産業総合=10000）
- series_type: 系列種別コード（VARCHAR、seasonally_adjusted / original）
- series_type_ja: 系列種別名（VARCHAR、季節調整済指数 / 原指数）
- year_month: 年月（VARCHAR、YYYYMM）
- year: 年（INTEGER）
- month: 月（INTEGER）
- index_value: 指数値（DOUBLE、2020年＝100）

品目（item_code / item_name）は「第３次産業総合」から日本標準産業分類の大分類・中分類・
個別業種までの階層を含みます。

### データ更新手順

main.py が経済産業省の公開 Excel（第３次産業活動指数 統計表・月次の季節調整済指数／原指数）を
取得して縦持ち CSV へ整形し、dbt build で指数テーブルを再生成する。
ビルドは `bash scripts/build.sh local` で実行する。

## ライセンス

経済産業省が公表する第３次産業活動指数を出典とし、[政府標準利用規約（第2.0版）](https://www.meti.go.jp/main/rules.html)に従う。縦持ちへの整形等の加工を行って利用している。
