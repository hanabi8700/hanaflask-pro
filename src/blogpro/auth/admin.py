from datetime import datetime

from extensions import db
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from auth.models import User
from auth.utils import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ユーザー一覧（管理者のみ）
@bp.route("/users")
@admin_required
def users():
    from blog.models import Post

    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(
        db.select(User).order_by(User.id),
        page=page,
        per_page=current_app.config["ADMIN_USERS_PER_PAGE"],
    )
    rows = db.session.execute(
        db.select(Post.userid, func.count()).group_by(Post.userid)
    ).all()
    counts = {userid: count for userid, count in rows}
    return render_template(
        "auth/admin_users.html", pagination=pagination, counts=counts
    )


# 削除フラグを付ける（ログイン不可になる。投稿はそのまま残る）
@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == g.user.id:
        flash("自分自身は削除できません。", "error")
    elif user.is_admin:
        flash("管理者アカウントは削除できません。", "error")
    elif user.is_deleted:
        flash("既に削除済みです。", "error")
    else:
        user.is_deleted = True
        user.deleted_at = datetime.now()
        db.session.commit()
        flash(
            f"ユーザー「{user.username}」に削除フラグを付けました（投稿は残ります）。",
            "success",
        )
    return redirect(url_for("admin.users", page=request.form.get("page", 1, type=int)))


# 削除フラグを外す（復活）
@bp.route("/users/<int:user_id>/restore", methods=["POST"])
@admin_required
def restore_user(user_id):
    user = db.get_or_404(User, user_id)
    if not user.is_deleted:
        flash("このユーザーは削除されていません。", "error")
    else:
        user.is_deleted = False
        user.deleted_at = None
        db.session.commit()
        flash(f"ユーザー「{user.username}」を復活しました。", "success")
    return redirect(url_for("admin.users", page=request.form.get("page", 1, type=int)))
