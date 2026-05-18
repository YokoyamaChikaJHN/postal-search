import io
import os
import zipfile

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="郵便番号検索", page_icon="📮", layout="wide")

CSV_PATH = "postal_codes.csv"
KEN_ALL_URL = "https://www.post.japanpost.jp/service/search/zipcode/download/kogaki/zip/ken_all.zip"

COLUMNS = [
    "lg_code", "old_zip", "zip",
    "pref_kana", "city_kana", "town_kana",
    "pref", "city", "town",
    "has_multi_zip", "has_koaza", "has_chome", "has_multi_town",
    "update_flag", "update_reason",
]


def _build_csv():
    resp = requests.get(KEN_ALL_URL, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csv_name = next(n for n in z.namelist() if n.upper().endswith(".CSV"))
        with z.open(csv_name) as f:
            df = pd.read_csv(f, encoding="cp932", header=None, names=COLUMNS, dtype=str)
    df["zip"] = df["zip"].str.zfill(7)
    df = df[["zip", "pref", "city", "town", "pref_kana", "city_kana", "town_kana"]]
    placeholder = "以下に掲載がない場合"
    df.loc[df["town"].str.startswith(placeholder, na=False), "town"] = ""
    df.loc[df["town_kana"].str.startswith("イカニケイサイガナイバアイ", na=False), "town_kana"] = ""
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")


@st.cache_data
def load_data():
    if not os.path.exists(CSV_PATH):
        with st.spinner("郵便番号データを準備中…（初回のみ）"):
            _build_csv()
    return pd.read_csv(CSV_PATH, dtype=str).fillna("")


df = load_data()

st.title("📮 郵便番号検索")
st.caption(f"全国 {len(df):,} 件のデータ（日本郵便 KEN_ALL）")

# ── 検索フォーム ───────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    zip_q = st.text_input("郵便番号", placeholder="例: 100-0001 / 1000001")
with col2:
    addr_q = st.text_input("住所（都道府県・市区町村・町域）", placeholder="例: 千代田 / 大阪市 / 新宿")
with col3:
    pref_list = ["（すべて）"] + sorted(df["pref"].unique().tolist())
    pref_q = st.selectbox("都道府県で絞り込み", pref_list)

# ── フィルタリング ─────────────────────────────────────────────────────────────
result = df.copy()

# 郵便番号：ハイフン除去して前方一致
if zip_q.strip():
    z = zip_q.strip().replace("-", "").replace("ー", "")
    result = result[result["zip"].str.startswith(z)]

# 住所：都道府県・市区町村・町域のいずれかに部分一致
if addr_q.strip():
    q = addr_q.strip()
    mask = (
        result["pref"].str.contains(q, na=False)
        | result["city"].str.contains(q, na=False)
        | result["town"].str.contains(q, na=False)
    )
    result = result[mask]

# 都道府県プルダウン
if pref_q != "（すべて）":
    result = result[result["pref"] == pref_q]

# ── 結果表示 ──────────────────────────────────────────────────────────────────
total = len(result)
if total == 0:
    st.warning("該当する郵便番号が見つかりません。")
    st.stop()

display_limit = 500
st.caption(f"{total:,} 件ヒット" + (f"（上位 {display_limit} 件を表示）" if total > display_limit else ""))

show = result.head(display_limit).rename(
    columns={
        "zip": "郵便番号",
        "pref": "都道府県",
        "city": "市区町村",
        "town": "町域",
        "pref_kana": "都道府県（カナ）",
        "city_kana": "市区町村（カナ）",
        "town_kana": "町域（カナ）",
    }
)

# 郵便番号を 〒XXX-XXXX 形式で表示
show["郵便番号"] = show["郵便番号"].apply(lambda z: f"〒{z[:3]}-{z[3:]}" if len(z) == 7 else z)

st.dataframe(
    show[["郵便番号", "都道府県", "市区町村", "町域", "都道府県（カナ）", "市区町村（カナ）", "町域（カナ）"]],
    use_container_width=True,
    hide_index=True,
)
