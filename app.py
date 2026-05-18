import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="郵便番号検索", page_icon="📮", layout="wide")

# スクリプトと同じディレクトリの CSV を確実に参照する
CSV_PATH = os.path.join(os.path.dirname(__file__), "postal_codes.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
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

# 何も入力されていなければ結果を表示しない
if not zip_q.strip() and not addr_q.strip() and pref_q == "（すべて）":
    st.info("郵便番号・住所・都道府県を入力または選択してください。")
    st.stop()

# ── 検索時だけ絞り込み ─────────────────────────────────────────────────────────
result = df

if zip_q.strip():
    z = zip_q.strip().replace("-", "").replace("ー", "")
    result = result[result["zip"].str.startswith(z)]

if addr_q.strip():
    q = addr_q.strip()
    result = result[
        result["pref"].str.contains(q, na=False)
        | result["city"].str.contains(q, na=False)
        | result["town"].str.contains(q, na=False)
    ]

if pref_q != "（すべて）":
    result = result[result["pref"] == pref_q]

# ── 結果表示 ──────────────────────────────────────────────────────────────────
total = len(result)
if total == 0:
    st.warning("該当する郵便番号が見つかりません。")
    st.stop()

display_limit = 500
st.caption(f"{total:,} 件ヒット" + (f"（上位 {display_limit} 件を表示）" if total > display_limit else ""))

show = result.head(display_limit).copy()
show["zip"] = show["zip"].apply(lambda z: f"〒{z[:3]}-{z[3:]}" if len(z) == 7 else z)
show = show.rename(columns={"zip": "郵便番号", "pref": "都道府県", "city": "市区町村", "town": "町域"})

st.dataframe(show[["郵便番号", "都道府県", "市区町村", "町域"]], use_container_width=True, hide_index=True)
