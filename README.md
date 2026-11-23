# DocuWorks Converter

DocuWorks（.xdw）ファイルを、TIFF・PDF・ビットマップ・JPEG に変換する Windows 用フリーソフトです。

DocuWorks 本体にも変換機能はありますが、文書データ単位でしか変換できません。DocuWorks Converter はフォルダ単位の一括変換に対応し、複数の .xdw ファイルをまとめて変換できます。

- 作者: Bridge Software
- バージョン: 1.0.3（2017年2月）
- ライセンス: MIT License

## 特長

- .xdw ファイルを TIFF / PDF / ビットマップ / JPEG の4形式に変換
- フォルダを指定して一括変換。ファイルをドラッグ＆ドロップするか、フォルダを指定するだけで変換できます
- 圧縮形式、解像度（10〜600dpi）、ページ、カラーを指定可能。ファイル名に「C」が含まれる場合は自動的にカラーで変換します
- よく使うフォルダを「変換元」「出力先」に各10件まで記憶
- DocuWorks Desk からのドラッグ＆ドロップにも対応
- 詳しい使い方は、配布版に同梱の使用説明書（PDF）に記載しています

## 動作環境

- Windows 7 / 8 / 8.1 / 10（32bit のみ）
- メモリ 512MB 以上、ハードディスク空き容量 50MB 以上
- **DocuWorks 7.0 以上**（変換処理に DocuWorks 本体が必要です）

## ダウンロード

- Vector（作者ページ）: https://www.vector.co.jp/vpack/browse/person/an060527.html
- GitHub Releases にも同じ版を公開予定です

## 開発・ビルド

- Python 3.4 + wxPython 製のシングルファイルアプリです（`DocuWorks Converter.pyw`）。DocuWorks の操作には xdwlib を使用しています
- ビルドは py2exe（`setup.py`）。アイコンは `options/image/` にあります

## ライセンス

MIT License で公開しています。`LICENSE` ファイルをご覧ください。

不具合報告や要望は、このリポジトリの Issues へお願いします。

---

※「DocuWorks」は富士フイルムビジネスイノベーション株式会社の登録商標です。本ソフトは Bridge Software が個人で開発した非公式ツールであり、動作には DocuWorks 本体が必要です。
