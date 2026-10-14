#!/virtual/hanacore/public_html/hanamaru8700.com/uvblog/.venv/bin/python

# https://hanamaru8700.com/uvblog/src/flask_app/
# --- エラー原因を画面に強制表示させるデバッグコード ---
import sys

print("Content-Type: text/plain; charset=UTF-8\n")
try:
    # ここに本来の処理（文字コード設定など）
    sys.stdout.reconfigure(encoding="utf-8")
except Exception as e:
    print(f"Error: {e}")
    sys.exit()
# --------------------------------------------------

# 正常な場合のHTML出力
html_body = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CGIテスト (Python)</title>
</head>
<body>
    <h1>こんにちは！Python CGIですPython 3.7以後</h1>
    <p>これは index.cgi から出力されたHTMLです。</p>
</body>
</html>"""

print(html_body)
