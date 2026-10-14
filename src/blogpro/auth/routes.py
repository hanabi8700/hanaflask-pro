from extensions import db
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from auth.models import User
from auth.utils import (
    login_required,
    safe_next,
    validate_password,
    validate_username,
)

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")


@bp.before_app_request
def load_logged_in_user():
    """セッションからログイン中ユーザーを g.user に読み込む（削除フラグ付きは無効）"""
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        user = db.session.get(User, user_id)
        if user is not None and not user.is_deleted:
            g.user = user
        else:
            session.pop("user_id", None)


@bp.app_context_processor
def inject_current_user():
    return {"current_user": g.get("user")}


def _find_user(username):
    return db.session.scalar(
        db.select(User).where(func.lower(User.username) == username.lower())
    )


# 新規登録
@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("blog.index"))

    form = {}
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("password_confirm") or ""
        form = {"username": username}

        errors = validate_username(username) + validate_password(password, confirm)
        if not errors and _find_user(username):
            errors.append("このユーザーIDは既に使用されています。")

        if not errors:
            user = User(username=username)
            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors.append("このユーザーIDは既に使用されています。")
            else:
                flash("登録しました。ログインしてください。", "success")
                return redirect(url_for("auth.login"))

        for e in errors:
            flash(e, "error")

    return render_template("auth/register.html", form=form)


# ログイン
@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("blog.index"))

    form = {}
    next_url = request.values.get("next", "")
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        form = {"username": username}

        user = _find_user(username) if username else None
        if not username or not password:
            flash("ユーザーIDとパスワードを入力してください。", "error")
        elif user is None or not user.check_password(password):
            flash("ユーザーIDまたはパスワードが正しくありません。", "error")
        elif user.is_deleted:
            flash(
                "このアカウントは利用できません。管理者にお問い合わせください。",
                "error",
            )
        else:
            session.clear()
            session["user_id"] = user.id
            flash("ログインしました。", "success")
            target = safe_next(next_url)
            if target:
                return redirect(request.script_root + target)
            return redirect(url_for("blog.index"))

    return render_template("auth/login.html", form=form, next_url=next_url)


# ログアウト
@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("ログアウトしました。", "success")
    return redirect(url_for("blog.index"))


# マイページ（登録日時・更新日時・投稿数）
@bp.route("/mypage")
@login_required
def mypage():
    from blog.models import Post  # 循環依存を避けるため関数内で import

    post_count = (
        db.session.scalar(
            db.select(func.count())
            .select_from(Post)
            .where(Post.userid == g.user.username)
        )
        or 0
    )
    return render_template("auth/mypage.html", user=g.user, post_count=post_count)


# パスワード変更（成功すると updated_at が自動で書き換わる）
@bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password") or ""
        new = request.form.get("new_password") or ""
        confirm = request.form.get("new_password_confirm") or ""

        errors = []
        if not current:
            errors.append("現在のパスワードを入力してください。")
        elif not g.user.check_password(current):
            errors.append("現在のパスワードが正しくありません。")
        errors += validate_password(new, confirm)
        if not errors and new == current:
            errors.append("新しいパスワードは現在のものと異なるものにしてください。")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/password.html")

        g.user.set_password(new)
        db.session.commit()  # onupdate により updated_at が自動更新される
        flash("パスワードを変更しました。", "success")
        return redirect(url_for("auth.mypage"))

    return render_template("auth/password.html")
