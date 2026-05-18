"""
日本郵便 KEN_ALL.CSV をダウンロードして postal_codes.csv に整形する。
実行: python prepare_data.py
"""
import io
import zipfile

import pandas as pd
import requests

URL = "https://www.post.japanpost.jp/service/search/zipcode/download/kogaki/zip/ken_all.zip"
OUTPUT = "postal_codes.csv"

COLUMNS = [
    "lg_code",        # 全国地方公共団体コード
    "old_zip",        # 旧郵便番号
    "zip",            # 郵便番号（7桁）
    "pref_kana",      # 都道府県名（カナ）
    "city_kana",      # 市区町村名（カナ）
    "town_kana",      # 町域名（カナ）
    "pref",           # 都道府県名
    "city",           # 市区町村名
    "town",           # 町域名
    "has_multi_zip",  # 一町域が二以上の郵便番号で表される場合
    "has_koaza",      # 小字毎に番地が起番されている町域
    "has_chome",      # 丁目を有する町域
    "has_multi_town", # 一郵便番号で二以上の町域を表す場合
    "update_flag",    # 更新の表示
    "update_reason",  # 変更理由
]

print("ダウンロード中…", end=" ", flush=True)
resp = requests.get(URL, timeout=60)
resp.raise_for_status()
data = resp.content
print("完了")

print("展開・読み込み中…", end=" ", flush=True)
with zipfile.ZipFile(io.BytesIO(data)) as z:
    csv_name = next(n for n in z.namelist() if n.upper().endswith(".CSV"))
    with z.open(csv_name) as f:
        df = pd.read_csv(
            f,
            encoding="cp932",
            header=None,
            names=COLUMNS,
            dtype=str,
        )
print("完了")

# 郵便番号をゼロ埋め7桁に統一
df["zip"] = df["zip"].str.zfill(7)

# 表示に使う列だけ残す
df = df[["zip", "pref", "city", "town", "pref_kana", "city_kana", "town_kana"]]

# 「以下に掲載がない場合」など不要なデフォルト町域名を空文字に置換
placeholder = "以下に掲載がない場合"
df.loc[df["town"].str.startswith(placeholder, na=False), "town"] = ""
df.loc[df["town_kana"].str.startswith("イカニケイサイガナイバアイ", na=False), "town_kana"] = ""

df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
print(f"保存完了: {OUTPUT}  ({len(df):,} 件)")
