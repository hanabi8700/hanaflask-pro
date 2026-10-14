#!/virtual/hanacore/public_html/hanamaru8700.com/uvblog/.venv/bin/python
####!/home/USERNAME/blog/.venv/bin/python
# -*- coding: utf-8 -*-
# 1行目の USERNAME を実際のユーザー名に書き換えてください（echo $HOME で確認）。
# 改行コードは LF、パーミッションは 755 にします。
import os
import sys
from pathlib import Path

# このフォルダの親（プロジェクトのルート）を検索パスに追加
project_root = str(Path(__file__).resolve().parent.parent)
# if project_root not in sys.path:
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

# 本番設定で起動（config.py の ProductionConfig を使用）
os.environ.setdefault("APP_ENV", "production")

from wsgiref.handlers import CGIHandler

from app import create_app


class StripScriptName:
    """SCRIPT_NAME から '/index.cgi' を除き、URLを /post/1 のように綺麗に保つ"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get("SCRIPT_NAME", "")
        if script_name.endswith("/index.cgi"):
            environ["SCRIPT_NAME"] = script_name[: -len("/index.cgi")]
        return self.app(environ, start_response)


application = StripScriptName(create_app())

if __name__ == "__main__":
    CGIHandler().run(application)
