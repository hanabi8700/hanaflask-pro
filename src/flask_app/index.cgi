#!/virtual/hanacore/public_html/hanamaru8700.com/uvblog/.venv/bin/python

import os
import sys
from pathlib import Path

# dvo フォルダの親（プロジェクトのルート）を検索パスに追加
project_root = str(Path(__file__).resolve().parent.parent)
#if project_root not in sys.path:
#    sys.path.append(project_root)
    
# 自分のアプリのディレクトリ
# sys.path: uvのPythonが import するモジュールやライブラリを探しに行く
# フォルダのリスト（一覧）です。
current_dir = os.path.dirname(__file__)
venv_site_packages = os.path.join(
    project_root, ".venv", "lib", "python3.10", "site-packages"
)
sys.path.insert(0, venv_site_packages)
# アプリケーションのパスを検索ルートに追加
sys.path.insert(1, current_dir)
from wsgiref.handlers import CGIHandler

from app import app as application

# コアサーバー（CGI環境）でうまく動かすための環境変数調整
os.environ["SCRIPT_NAME"] = "/index.cgi"

if __name__ == "__main__":
    CGIHandler().run(application)
