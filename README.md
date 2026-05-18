# 📮 郵便番号検索

日本郵便の[郵便番号データ（KEN_ALL）](https://www.post.japanpost.jp/zipcode/dl/kogaki-zip.html)を使った全国郵便番号検索 Streamlit アプリです。

## 機能

- **郵便番号**で検索（ハイフンあり・なし両対応、前方一致）
- **住所**（都道府県・市区町村・町域）でキーワード検索
- **都道府県**プルダウンで絞り込み
- 全国約 **12 万件**のデータを即時検索

## セットアップ

```bash
pip install -r requirements.txt
python prepare_data.py   # KEN_ALL.CSV をダウンロードして整形
streamlit run app.py
```

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/)

Codespaces を起動すると自動でデータのダウンロード・整形・アプリ起動まで行われます。

## データ出典

- [日本郵便 郵便番号データダウンロード](https://www.post.japanpost.jp/zipcode/dl/kogaki-zip.html)
