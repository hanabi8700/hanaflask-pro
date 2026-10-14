import os
import sys

# 新しいパスを設定
new_path = "/path/to/your/module"

# 既存のPYTHONPATHに新しいパスを追加（重複確認あり）
if "PYTHONPATH" in os.environ:
    paths = os.environ["PYTHONPATH"].split(os.pathsep)
    if new_path not in paths:
        os.environ["PYTHONPATH"] = new_path + os.pathsep + os.environ["PYTHONPATH"]
else:
    os.environ["PYTHONPATH"] = new_path

# 設定されたPYTHONPATHを確認
print(f"Environ:{os.environ['PYTHONPATH']}")

# 実際にsys.pathに反映されていることを確認
print(f"sys_path:{sys.path}")

# パスを追加する前に重複確認をする関数
def add_path_if_not_exists(index, path):
    if path not in sys.path:
        if index < len(sys.path):
            sys.path.insert(index, path)
        else:
            sys.path.append(path)


# 最優先で検索されるパスを追加
add_path_if_not_exists(0, "/path/to/high/priority")

# 2番目に優先されるパスを追加
add_path_if_not_exists(1, "/path/to/medium/priority")

# 最後に検索されるパスを追加
add_path_if_not_exists(len(sys.path), "/path/to/low/priority")

current_dir = os.path.dirname(__file__)
venv_site_packages = os.path.join(
    current_dir, ".venv", "lib", "python3.10", "site-packages"
)
sys.path.insert(0, venv_site_packages)

# 追加されたパスを確認
print(f"\nsys_path:{sys.path}")
