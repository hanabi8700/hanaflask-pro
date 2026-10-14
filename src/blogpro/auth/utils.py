import re
from functools import wraps
from urllib.parse import urlparse

from flask import abort, flash, g, redirect, request, url_for

USERNAME_RE = re.compile(r"[A-Za-z0-9_]{3,30}")
MIN_PASSWORD = 8
MAX_PASSWORD = 128


def validate_username(username):
    errors = []
    if not username:
        errors.append("ユーザーIDを入力してください。")
    elif any(c.isspace() for c in username):
        errors.append("ユーザーIDに空白は使用できません。")
    elif not USERNAME_RE.fullmatch(username):
        errors.append("ユーザーIDは半角英数字とアンダースコアの3〜30文字で入力してください。")
    return errors


def validate_password(password, confirm=None):
    errors = []
    if not password:
        errors.append("パスワードを入力してください。")
    else:
        if any(c.isspace() for c in password):
            errors.append("パスワードに空白は使用できません。")
        if len(password) < MIN_PASSWORD:
            errors.append(f"パスワードは{MIN_PASSWORD}文字以上で入力してください。")
        if len(password) > MAX_PASSWORD:
            errors.append(f"パスワードは{MAX_PASSWORD}文字以内で入力してください。")
    if confirm is not None and password != confirm:
        errors.append("パスワード（確認）が一致しません。")
    return errors


def safe_next(target):
    """オープンリダイレクト対策: アプリ内の相対パスのみ許可"""
    if not target or not target.startswith("/") or target.startswith("//"):
        return None
    if "\\" in target or "\n" in target or "\r" in target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    return target


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            flash("ログインしてください。", "error")
            next_path = request.full_path.rstrip("?") if request.method == "GET" else None
            return redirect(url_for("auth.login", next=next_path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = g.get("user")
        if user is None:
            flash("ログインしてください。", "error")
            return redirect(url_for("auth.login"))
        if not user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
