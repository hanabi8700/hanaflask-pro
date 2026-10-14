from flask import (
    Blueprint, abort, current_app, flash, g, redirect, render_template,
    request, url_for,
)
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from auth.utils import login_required
from blog.models import Post
from blog.utils import clean_post_fields, delete_image, escape_like, save_image
from extensions import db

bp = Blueprint("blog", __name__)


def _upload_dir():
    return current_app.config["UPLOAD_FOLDER"]


def _check_permission(post):
    """投稿者本人か管理者のみ編集・削除できる"""
    if not (g.user.is_admin or g.user.username == post.userid):
        abort(403)


def _try_save_image(errors):
    """アップロード画像があれば保存。(ファイル名 or None) を返し、問題は errors に追加"""
    file = request.files.get("image")
    if errors or not file or not file.filename:
        return None
    name, error = save_image(
        file, _upload_dir(), current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )
    if error:
        errors.append(error)
    return name


# 一覧 + 検索 + ページネーション (Read)
@bp.route("/")
def index():
    q = (request.args.get("q") or "").strip()[:100]
    userid = (request.args.get("userid") or "").strip()[:50]
    page = request.args.get("page", 1, type=int)

    stmt = db.select(Post)
    if userid:
        stmt = stmt.where(Post.userid == userid)
    for keyword in q.split()[:5]:  # 空白（全角含む）区切りの AND 検索
        pattern = f"%{escape_like(keyword)}%"
        stmt = stmt.where(
            or_(
                Post.title.like(pattern, escape="\\"),
                Post.body.like(pattern, escape="\\"),
            )
        )
    stmt = stmt.order_by(Post.created_at.desc(), Post.id.desc())

    pagination = db.paginate(
        stmt, page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    params = {k: v for k, v in (("q", q), ("userid", userid)) if v}
    return render_template(
        "index.html",
        pagination=pagination,
        posts=pagination.items,
        q=q,
        userid=userid,
        params=params,
    )


# 詳細 (Read)
@bp.route("/post/<int:post_id>")
def detail(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template("detail.html", post=post)


# 新規作成 (Create)
@bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title, body, errors = clean_post_fields(
            request.form.get("title"), request.form.get("body")
        )
        image_name = _try_save_image(errors)

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "form.html", post=None, form={"title": title, "body": body}
            )

        post = Post(
            userid=g.user.username, title=title, body=body, image_filename=image_name
        )
        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            delete_image(_upload_dir(), image_name)
            flash("保存に失敗しました。もう一度お試しください。", "error")
            return render_template(
                "form.html", post=None, form={"title": title, "body": body}
            )
        flash("記事を作成しました。", "success")
        return redirect(url_for("blog.detail", post_id=post.id))

    return render_template("form.html", post=None, form={})


# 編集 (Update)
@bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = db.get_or_404(Post, post_id)
    _check_permission(post)

    if request.method == "POST":
        title, body, errors = clean_post_fields(
            request.form.get("title"), request.form.get("body")
        )
        old_image = post.image_filename
        new_image = _try_save_image(errors)

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "form.html", post=post, form={"title": title, "body": body}
            )

        post.title = title
        post.body = body
        if new_image:
            post.image_filename = new_image
        elif request.form.get("delete_image"):
            post.image_filename = None

        try:
            db.session.commit()  # updated_at は onupdate で自動更新
        except SQLAlchemyError:
            db.session.rollback()
            delete_image(_upload_dir(), new_image)
            flash("保存に失敗しました。もう一度お試しください。", "error")
            return render_template(
                "form.html", post=post, form={"title": title, "body": body}
            )

        if old_image and post.image_filename != old_image:
            delete_image(_upload_dir(), old_image)
        flash("記事を更新しました。", "success")
        return redirect(url_for("blog.detail", post_id=post.id))

    return render_template(
        "form.html", post=post, form={"title": post.title, "body": post.body}
    )


# 削除 (Delete)
@bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = db.get_or_404(Post, post_id)
    _check_permission(post)
    image_name = post.image_filename
    db.session.delete(post)
    db.session.commit()
    delete_image(_upload_dir(), image_name)
    flash("記事を削除しました。", "success")
    return redirect(url_for("blog.index"))
