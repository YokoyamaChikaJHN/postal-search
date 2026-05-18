import requests
import streamlit as st

st.set_page_config(page_title="郵便番号検索", page_icon="📮", layout="wide")

ZIPCLOUD = "https://zipcloud.ibsnet.co.jp/api/search"
HEARTRAILS = "https://geoapi.heartrails.com/api/json"

PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]


@st.cache_data(ttl=86400, show_spinner=False)
def zip_to_address(zipcode: str) -> list[dict]:
    r = requests.get(ZIPCLOUD, params={"zipcode": zipcode, "limit": 20}, timeout=10)
    r.raise_for_status()
    return r.json().get("results") or []


@st.cache_data(ttl=86400, show_spinner=False)
def get_cities(pref: str) -> list[str]:
    r = requests.get(HEARTRAILS, params={"method": "getCities", "prefecture": pref}, timeout=10)
    r.raise_for_status()
    locs = r.json().get("response", {}).get("location", [])
    return [loc["city"] for loc in locs]


@st.cache_data(ttl=86400, show_spinner=False)
def get_towns(pref: str, city: str) -> list[dict]:
    r = requests.get(HEARTRAILS, params={"method": "getTowns", "prefecture": pref, "city": city}, timeout=10)
    r.raise_for_status()
    return r.json().get("response", {}).get("location", [])


def fmt_zip(z: str) -> str:
    return f"〒{z[:3]}-{z[3:]}" if len(z) == 7 else z


st.title("📮 郵便番号検索")

tab_zip, tab_addr = st.tabs(["郵便番号 → 住所", "住所 → 郵便番号（逆引き）"])

# ── タブ1: 郵便番号 → 住所 ────────────────────────────────────────────────────
with tab_zip:
    zip_q = st.text_input("郵便番号を入力", placeholder="例: 1000001 / 100-0001")
    if zip_q.strip():
        z = zip_q.strip().replace("-", "").replace("ー", "")
        if not z.isdigit() or len(z) < 3:
            st.warning("数字3桁以上で入力してください。")
        else:
            with st.spinner("検索中…"):
                try:
                    results = zip_to_address(z)
                except requests.RequestException as e:
                    st.error(f"APIエラー: {e}")
                    results = []
            if results:
                st.caption(f"{len(results)} 件")
                st.dataframe(
                    [{"郵便番号": fmt_zip(r["zipcode"]), "都道府県": r["address1"],
                      "市区町村": r["address2"], "町域": r["address3"]} for r in results],
                    use_container_width=True, hide_index=True,
                )
            else:
                st.warning("該当する住所が見つかりません。")

# ── タブ2: 住所 → 郵便番号（逆引き）─────────────────────────────────────────
with tab_addr:
    st.caption("都道府県・市区町村を選択すると郵便番号を逆引きします。")
    col1, col2 = st.columns(2)

    with col1:
        pref = st.selectbox("都道府県", ["（選択してください）"] + PREFECTURES)

    cities: list[str] = []
    if pref != "（選択してください）":
        with st.spinner("市区町村を取得中…"):
            try:
                cities = get_cities(pref)
            except requests.RequestException as e:
                st.error(f"APIエラー: {e}")

    with col2:
        city_options = ["（選択してください）"] + cities
        city = st.selectbox("市区町村", city_options, disabled=(not cities))

    if pref != "（選択してください）" and city != "（選択してください）":
        with st.spinner("町域・郵便番号を取得中…"):
            try:
                towns = get_towns(pref, city)
            except requests.RequestException as e:
                st.error(f"APIエラー: {e}")
                towns = []

        town_q = st.text_input("町域で絞り込み（任意）", placeholder="例: 千代田 / 丸の内")
        if town_q.strip():
            towns = [t for t in towns if town_q.strip() in t.get("town", "")]

        if towns:
            st.caption(f"{len(towns)} 件")
            st.dataframe(
                [{"郵便番号": fmt_zip(t["postal"]), "都道府県": t["prefecture"],
                  "市区町村": t["city"], "町域": t["town"]} for t in towns],
                use_container_width=True, hide_index=True,
            )
        else:
            st.warning("該当する町域が見つかりません。")
