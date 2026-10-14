"""管理者ユーザー作成スクリプト（本番用）

使い方:
    uv run python src/create_admin.py <ユーザーID>
    # 本番サーバーでは:  APP_ENV=production ~/blog/.venv/bin/python create_admin.py <ユーザーID>
    # APP_ENV=production ~/public_html/hanamaru8700.com/uvblog/.venv/bin/python create_adm
in.py hanaadgm
既に同名ユーザーがいる場合は、管理者に昇格し、削除フラグを外してパスワードを更新します。
"""

import argparse
import sys
from getpass import getpass

from app import create_app
from auth.models import User
from auth.utils import validate_password, validate_username
from extensions import db
from sqlalchemy import func


def main():
    parser = argparse.ArgumentParser(description="管理者ユーザーを作成")
    parser.add_argument("username", help="ユーザーID（半角英数字と_、3〜30文字）")
    args = parser.parse_args()

    errors = validate_username(args.username)
    if errors:
        sys.exit("\n".join(errors))

    password = getpass("パスワード: ")
    confirm = getpass("パスワード（確認）: ")
    errors = validate_password(password, confirm)
    if errors:
        sys.exit("\n".join(errors))

    app = create_app()
    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(func.lower(User.username) == args.username.lower())
        )
        if user is None:
            user = User(username=args.username)
            db.session.add(user)
            action = "作成"
        else:
            action = "更新"
        user.is_admin = True
        user.is_deleted = False
        user.deleted_at = None
        user.set_password(password)
        db.session.commit()
        print(f"管理者ユーザー「{user.username}」を{action}しました。")


if __name__ == "__main__":
    main()
