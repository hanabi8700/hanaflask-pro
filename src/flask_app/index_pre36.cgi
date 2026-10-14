#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# https://hanamaru8700.com/uvblog/src/flask_app/

import sys
import io

# Python 3.6以前でも動作する文字コード設定（標準出力をUTF-8に変更）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ブラウザに「これからHTMLを送ります」と伝えるお約束の行
print("Content-Type: text/html; charset=UTF-8\n")

# 表示したいHTMLを出力する
html_body = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CGIテスト (Python)</title>
</head>
<body>
    <h1>こんにちは！Python CGIです Python 3.6以前</h1>
    <p>これは index.cgi から出力されたHTMLです。</p>
</body>
</html>"""

print(html_body)
