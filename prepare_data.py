"""
日本郵便 KEN_ALL.CSV をダウンロードして postal_codes.csv に整形する。
実行: python prepare_data.py
      python prepare_data.py --force  # 既存ファイルを上書き
"""
import io
import os
import sys
import zipfile

import pandas as pd
import requests

URL = "https://www.post.japanpost.jp/service/search/zipcode/download/kogaki/zip/ken_all.zip"
OUTPUT = os.path.join(os.path.dirname(__file__), "postal_codes.csv")

COLUMNS = [
    "lg_code", "old_zip", "zip",
    "pref_kana", "city_kana", "town_kana",
    "pref", "city", "town",
    "has_multi_zip", "has_koaza", "has_chome", "has_multi_town",
    "update_flag", "update_reason",
]

force = "--force" in sys.argv
if os.path.exists(OUTPUT) and not force:
    print(f"{OUTPUT} は既に存在するためスキップします。--force で上書きできます。")
    sys.exit(0)

print("ダウンロード中…", end=" ", flush=True)
resp = requests.get(URL, timeout=60)
resp.raise_for_status()
print("完了")

print("展開・読み込み中…", end=" ", flush=True)
with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
    csv_name = next(n for n in z.namelist() if n.upper().endswith(".CSV"))
    with z.open(csv_name) as f:
        df = pd.read_csv(f, encoding="cp932", header=None, names=COLUMNS, dtype=str)
print("完了")

df["zip"] = df["zip"].str.zfill(7)

# 必要最小限の4列のみ保持（カナ列は除外してファイルサイズを削減）
df = df[["zip", "pref", "city", "town"]]

# 「以下に掲載がない場合」などのデフォルト町域名を空文字に置換
df.loc[df["town"].str.startswith("以下に掲載がない場合", na=False), "town"] = ""

df.to_csv(OUTPUT, index=False, encoding="utf-8")
print(f"保存完了: {OUTPUT}  ({len(df):,} 件, {os.path.getsize(OUTPUT)//1024:,} KB)")
