import hmac
import os
import secrets

from config import INSTANCE_DIR, DevelopmentConfig, ProductionConfig
from extensions import db
from flask import Flask, abort, render_template, request, session

CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

ERROR_PAGES = {
    400: (
        "不正なリクエストです",
        "フォームの有効期限が切れた可能性があります。ページを再読み込みして、もう一度お試しください。",
    ),
    403: ("権限がありません", "このページを表示・操作する権限がありません。"),
    404: (
        "ページが見つかりません",
        "お探しのページは存在しないか、移動または削除された可能性があります。",
    ),
    413: (
        "ファイルが大きすぎます",
        "アップロードできるサイズの上限（5MB）を超えています。",
    ),
    500: (
        "サーバーエラー",
        "一時的な問題が発生しました。しばらくしてからもう一度お試しください。",
    ),
}


def _csrf_token():
    """セッションごとの CSRF トークン（テンプレートの csrf_token() から使う）"""
    token = session.get("_csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf"] = token
    return token


def _csrf_protect():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = (request.form.get("csrf_token") or "").encode("utf-8")
        expected = (session.get("_csrf") or "").encode("utf-8")
        if not expected or not hmac.compare_digest(sent, expected):
            abort(400)


def _render_error(error):
    code = getattr(error, "code", None)
    if code not in ERROR_PAGES:
        code = 500
    title, message = ERROR_PAGES[code]
    return render_template("error.html", code=code, title=title, message=message), code

# ==========================================
# 【自作】.envファイルから環境変数を読み込む関数
# ==========================================
def load_env_file():
    # Flaskアプリと同じ階層にある「.env」ファイルを探す
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                # 空行やコメント行（#）を無視する
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # 「キー=値」の形式を分割して環境変数に注入
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()




def create_app(config_name=None):
    # 起動時に実行して、.envの中身をシステム環境に登録
    load_env_file()

    config_name = config_name or os.environ.get("APP_ENV", "development")
    config_class = CONFIGS.get(config_name, DevelopmentConfig)


    app = Flask(__name__, instance_path=INSTANCE_DIR)
    app.config.from_object(config_class)

    #print(f"{os.environ.get('FLASK_SECRET_KEY')}")
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY が未設定です。環境変数 SECRET_KEY か "
            "instance/secret_key.txt に設定してください。"
        )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # static/uploads

    db.init_app(app)

    from auth.admin import bp as admin_bp
    from auth.routes import bp as auth_bp
    from blog.routes import bp as blog_bp
    from blog.utils import format_datetime, render_markdown

    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    app.jinja_env.filters["markdown"] = render_markdown
    app.jinja_env.filters["dt"] = format_datetime
    app.jinja_env.globals["csrf_token"] = _csrf_token

    app.before_request(_csrf_protect)
    for code in ERROR_PAGES:
        app.register_error_handler(code, _render_error)

    with app.app_context():
        import auth.models  # noqa: F401  (テーブル定義を読み込む)
        import blog.models  # noqa: F401

        db.create_all()

    return app


def create3_app(config_name=None):

    config_name = config_name or os.environ.get("APP_ENV", "development")
    config_class = CONFIGS.get(config_name, DevelopmentConfig)

    # 起動時に実行して、.envの中身をシステムに登録
    load_env_file()

    app = Flask(__name__, instance_path=INSTANCE_DIR)
    app.config.from_object(config_class)
    secret_key = {
        os.environ.get("FLASK_SECRET_KEY")
        or os.environ.get("REDIRECT_FLASK_SECRET_KEY")
        or os.environ.get("HTTP_FLASK_SECRET_KEY")
    }
    app.config["SECRET_KEY"] = secret_key

    """_summary_
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY が未設定です。環境変数 SECRET_KEY か "
            "instance/secret_key.txt に設定してください。"
        )

    """

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # static/uploads

    @app.route("/")
    def hello():
        current_dir = os.path.dirname(__file__)
        print(f"{current_dir},")
        print(f"{config_name},{config_class},{app.config['SECRET_KEY']}")
        # 届いている全ての環境変数をコンソールに出力して確認
        import pprint

        pprint.pprint(dict(os.environ))
        print("Hello from Flask inside CORESERVER with uv!")
        return ""

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
