# 📮 郵便番号検索

外部 API を使った全国郵便番号検索 Streamlit アプリです。データファイル不要で高速に起動します。

## 機能

| タブ | 方向 | 使用 API |
|---|---|---|
| 郵便番号 → 住所 | 郵便番号 3〜7桁で住所を検索 | [zipcloud](https://zipcloud.ibsnet.co.jp/doc/api) |
| 住所 → 郵便番号（逆引き） | 都道府県・市区町村を選択して郵便番号を逆引き | [HeartRails Geo API](https://geoapi.heartrails.com/) |

## セットアップ

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/)

## データ出典

- [zipcloud 郵便番号検索 API](https://zipcloud.ibsnet.co.jp/doc/api)
- [HeartRails Geo API](https://geoapi.heartrails.com/)
