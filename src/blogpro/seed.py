"""テスト用ダミーデータ生成スクリプト

使い方（プロジェクトルートで）:
    uv run python src/seed.py            # ダミー記事50件を追加
    uv run python src/seed.py --reset    # 既存の投稿を全削除して50件作り直す
    uv run python src/seed.py --count 120

開発用のユーザー（admin / alice / bob / carol）も無ければ作成します。
本番設定（APP_ENV=production）では --force を付けない限り実行しません。
"""
import argparse
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import func

from app import create_app
from auth.models import User
from blog.models import Post
from extensions import db

# (ユーザーID, パスワード, 管理者か) ※開発専用。本番では使わないこと
SEED_USERS = [
    ("admin", "Admin12345", True),
    ("alice", "Password123", False),
    ("bob", "Password123", False),
    ("carol", "Password123", False),
]

TOPICS = [
    "Flask入門", "SQLiteのコツ", "Markdownの書き方", "Blueprintで整理する",
    "ページネーションの実装", "検索機能のメモ", "画像アップロードの注意点",
    "uv環境の構築", "デプロイ手順メモ", "Jinja2テンプレート",
]
KEYWORDS = ["flask", "sqlite", "markdown", "blueprint", "paginate", "search", "upload", "uv", "deploy", "jinja2"]
QUOTES = [
    "小さく作って、動かして、直す。",
    "テストデータは多めに用意すると見えるものがある。",
    "まずは動くものから。",
    "入力チェックは必ずサーバー側でも行う。",
]


def ensure_users():
    users = []
    for username, password, is_admin in SEED_USERS:
        user = db.session.scalar(
            db.select(User).where(func.lower(User.username) == username.lower())
        )
        if user is None:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            print(f"  ユーザー作成: {username} / {password}")
        users.append(user)
    db.session.commit()
    return users


def main():
    parser = argparse.ArgumentParser(description="ダミーデータ生成")
    parser.add_argument("--count", type=int, default=50, help="作成する記事数（既定: 50）")
    parser.add_argument("--reset", action="store_true", help="既存の投稿を全削除してから作成")
    parser.add_argument("--force", action="store_true", help="本番設定でも実行する")
    args = parser.parse_args()

    app = create_app()
    if app.config.get("APP_ENV") == "production" and not args.force:
        sys.exit("本番設定では実行しません（どうしても必要なら --force）。")

    with app.app_context():
        users = ensure_users()

        if args.reset:
            db.session.execute(db.delete(Post))
            db.session.commit()
            print("  既存の投稿を削除しました。")

        rng = random.Random(42)
        now = datetime.now()
        posts = []
        for n in range(1, args.count + 1):
            idx = rng.randrange(len(TOPICS))
            owner = rng.choice(users)
            created = now - timedelta(
                days=rng.randint(0, 60), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
            )
            updated = min(now, created + timedelta(hours=rng.randint(0, 72)))
            body = (
                f"# {TOPICS[idx]}\n\n"
                f"これは **テスト用のダミー記事** です（No.{n}）。\n\n"
                f"## ポイント\n\n"
                f"- 項目1: *Flask* と Flask-SQLAlchemy\n"
                f"- 項目2: キーワード `{KEYWORDS[idx]}`\n"
                f"- 項目3: ページネーションと検索の確認\n\n"
                f"> {rng.choice(QUOTES)}\n"
            )
            posts.append(
                Post(
                    userid=owner.username,
                    title=f"ダミー記事 {n:02d}: {TOPICS[idx]}",
                    body=body,
                    created_at=created,
                    updated_at=updated,
                )
            )
        db.session.add_all(posts)
        db.session.commit()
        print(f"  ダミー記事を {len(posts)} 件作成しました。")


if __name__ == "__main__":
    main()
