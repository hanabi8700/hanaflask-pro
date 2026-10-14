import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # src/
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")      # src/instance
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")


def _read_secret_key_file():
    """instance/secret_key.txt から SECRET_KEY を読む（無ければ None）"""
    path = os.path.join(INSTANCE_DIR, "secret_key.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-only-change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "blog.db")

    # アップロード
    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # ページネーション
    POSTS_PER_PAGE = 10
    ADMIN_USERS_PER_PAGE = 20

    # セッション
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(BaseConfig):
    APP_ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "blog_dev.db")


class ProductionConfig(BaseConfig):
    APP_ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "blog.db")
    # 本番は環境変数 SECRET_KEY か instance/secret_key.txt が必須（無ければ起動時にエラー）
    SECRET_KEY = os.environ.get("SECRET_KEY") or _read_secret_key_file()
    # HTTPS で運用する場合は環境変数 SESSION_COOKIE_SECURE=1 を設定
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE") == "1"
