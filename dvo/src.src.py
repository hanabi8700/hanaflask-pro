import sys
from pathlib import Path

# dvo フォルダの親（プロジェクトのルート）を検索パスに追加
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

print(f"{project_root}")

# パスが通ったのでインポートできるようになります
# from src.config import INSTANCE_DIR, config_by_name
from src.src.blog import create_app

# $ uv run src.src.py
if __name__ == "__main__":
    # app.run(debug=True)
    create_app().run(debug=True)
