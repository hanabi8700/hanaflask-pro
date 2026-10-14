import html
import os
import re
import uuid

import markdown as md
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup

TITLE_MAX = 200
BODY_MAX = 20000

MD_EXTENSIONS = ["fenced_code", "tables", "nl2br", "sane_lists"]

# --- Markdown の安全化（外部のサニタイズ用ライブラリは使わず、Markdown 自身の仕組みで行う）---
# 1. 生の HTML は無効化（<script> などは文字として表示される）
# 2. 生成された要素の属性を許可リスト方式で絞る
# 3. リンク/画像の URL は http / https / mailto / 相対パスのみ許可
ALLOWED_ATTRS = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "code": {"class"},
    "th": {"style", "align"},
    "td": {"style", "align"},
}
SAFE_SCHEMES = {"http", "https", "mailto"}
_CTRL_RE = re.compile(r"[\x00-\x20\x7f]+")
_SCHEME_RE = re.compile(r"([A-Za-z][A-Za-z0-9+.\-]*):")
_ALIGN_STYLE_RE = re.compile(r"text-align:\s*(left|right|center);?")
_CODE_CLASS_RE = re.compile(r"language-[A-Za-z0-9_+\-]+")


def _is_safe_url(url):
    # HTML エンティティや空白・制御文字による偽装（java&#115;cript: など）を除いて判定
    candidate = _CTRL_RE.sub("", html.unescape(url or ""))
    match = _SCHEME_RE.match(candidate)
    return match is None or match.group(1).lower() in SAFE_SCHEMES


class _SafeTreeprocessor(Treeprocessor):
    def run(self, root):
        for el in root.iter():
            allowed = ALLOWED_ATTRS.get(el.tag, set())
            for name in list(el.attrib):
                value = el.get(name) or ""
                if name not in allowed:
                    del el.attrib[name]
                elif name in ("href", "src") and not _is_safe_url(value):
                    del el.attrib[name]
                elif name == "style" and not _ALIGN_STYLE_RE.fullmatch(value.strip()):
                    del el.attrib[name]
                elif name == "class" and not _CODE_CLASS_RE.fullmatch(value):
                    del el.attrib[name]


class _SafeMarkdown(Extension):
    def extendMarkdown(self, md_instance):
        md_instance.preprocessors.deregister("html_block", strict=False)
        md_instance.inlinePatterns.deregister("html", strict=False)
        md_instance.treeprocessors.register(
            _SafeTreeprocessor(md_instance), "safe_output", 0
        )


def render_markdown(text):
    """Markdown → 安全な HTML（Jinja2 フィルタ `markdown` として使用）"""
    html_text = md.markdown(text or "", extensions=MD_EXTENSIONS + [_SafeMarkdown()])
    return Markup(html_text)


def format_datetime(value, fmt="%Y-%m-%d %H:%M"):
    """Jinja2 フィルタ `dt`"""
    return value.strftime(fmt) if value else ""


def escape_like(keyword):
    """LIKE 検索用に % _ \\ をエスケープ"""
    return keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def clean_post_fields(title, body):
    """入力チェック。(整形後title, 整形後body, エラー一覧) を返す"""
    title = (title or "").strip()
    body = (body or "").strip()
    errors = []

    if not title:
        errors.append("タイトルを入力してください（空白のみは不可）。")
    elif len(title) > TITLE_MAX:
        errors.append(f"タイトルは{TITLE_MAX}文字以内で入力してください。")
    elif "\n" in title or "\r" in title:
        errors.append("タイトルに改行は使用できません。")

    if not body:
        errors.append("本文を入力してください（空白のみは不可）。")
    elif len(body) > BODY_MAX:
        errors.append(f"本文は{BODY_MAX}文字以内で入力してください。")

    return title, body, errors


def _looks_like_image(head, ext):
    if ext == "png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in ("jpg", "jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == "gif":
        return head.startswith((b"GIF87a", b"GIF89a"))
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    return False


def save_image(file_storage, upload_dir, allowed_extensions):
    """画像を検証して保存。(保存ファイル名, エラー文) を返す"""
    filename = file_storage.filename or ""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in allowed_extensions:
        return None, "画像は png / jpg / jpeg / gif / webp のみアップロードできます。"

    head = file_storage.stream.read(16)
    file_storage.stream.seek(0)
    if not _looks_like_image(head, ext):
        return None, "画像ファイルの内容が正しくありません。"

    os.makedirs(upload_dir, exist_ok=True)  # static/uploads が無ければ作る
    saved_ext = "jpg" if ext == "jpeg" else ext
    name = f"{uuid.uuid4().hex}.{saved_ext}"
    file_storage.save(os.path.join(upload_dir, name))
    return name, None


def delete_image(upload_dir, filename):
    if not filename:
        return
    try:
        os.remove(os.path.join(upload_dir, os.path.basename(filename)))
    except OSError:
        pass
