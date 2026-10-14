#!/virtual/hanacore/public_html/hanamaru8700.com/cgi-bin/hanauv/.venv/bin/python

import os
import sys

# FlaskアプリがあるディレクトリをPythonの検索パスに追加
sys.path.insert(
    0, "/virtual/hanacore/public_html/hanamaru8700.com/cgi-bin/hanauv/src/src"
)

from wsgiref.handlers import CGIHandler

# from app import app
from src.src.blog import create_app

app = create_app()

# コアサーバー（CGI環境）でうまく動かすための環境変数調整
os.environ["SCRIPT_NAME"] = "/index.cgi"

if __name__ == "__main__":
    #CGIHandler().run(app)
    app.run()
