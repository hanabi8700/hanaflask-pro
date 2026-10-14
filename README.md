# blog

Flask + Flask-SQLAlchemy（SQLite）+ Blueprint で作った、CRUD 付きブログ（uv / Python 3.10 以上）。

## 機能

- 記事の作成・一覧・詳細・編集・削除（Markdown 本文。生のHTMLは無効化し、危険なURLは除去）
- 一覧にタイトル・userid・変更日、ページネーション（10件/ページ）
- 検索窓: タイトル・本文のキーワード（空白区切りで AND）＋ userid での絞り込み
- 画像アップロード（png / jpg / gif / webp、5MBまで。`static/uploads` が無ければ自動作成）
- ユーザー登録・ログイン・ログアウト（`auth/` に分離）、マイページ（登録日時・更新日時・投稿数）
- パスワード変更（変更すると `updated_at` が自動で書き換わる）
- 管理者機能: ユーザー一覧、削除フラグ（ログイン不可・投稿は残る）、復活
- パスワード欄の「👁」で表示/非表示を切り替え
- 404 などのカスタムエラーページ（`error.html`）
- CSRF トークン、入力チェック（空白のみ不可・エラー表示）

## 構成

```
blog/
├─ pyproject.toml / .python-version
└─ src/
   ├─ app.py            アプリケーションファクトリ（エラーページ・CSRF）
   ├─ config.py         BaseConfig / DevelopmentConfig / ProductionConfig
   ├─ extensions.py     db
   ├─ seed.py           ダミーデータ生成（既定50件）
   ├─ create_admin.py   管理者ユーザー作成（本番用）
   ├─ index.cgi / .htaccess   デプロイ用
   ├─ blog/             記事（models / routes / utils）
   ├─ auth/             認証・管理者（models / routes / admin / utils / templates）
   ├─ templates/        base.html, index.html, detail.html, form.html, error.html, _macros.html
   ├─ static/           css/style.css, js/password-toggle.js, uploads/
   └─ instance/         SQLite DB（開発: blog_dev.db / 本番: blog.db）
```

## ローカル開発

```bash
uv sync
uv run python src/seed.py            # ダミー記事50件 + 開発用ユーザーを作成
uv run flask --app src/app run --debug
```

http://127.0.0.1:5000/ を開く。`seed.py` が作る開発用ユーザー:

| ユーザーID | パスワード | 権限 |
|---|---|---|
| admin | Admin12345 | 管理者 |
| alice / bob / carol | Password123 | 一般 |

`uv run python src/seed.py --reset` で投稿を消して作り直せます。

環境は `APP_ENV`（`development` が既定 / `production`）で切り替えます。

## CORESERVER へのデプロイ（Apache + CGI）

### サーバー側レイアウト

```
~/blog/               プロジェクトルート（公開フォルダの外）
├─ pyproject.toml
├─ uv.lock
├─ .python-version
└─ .venv/             uv sync で作成

(公開フォルダ)/        src の中身（index.cgi, .htaccess, app.py, ...）
```

### 手順

1. 手元で `uv lock` を実行し、`uv.lock` を作る
2. アップロード

   ```bash
   rsync -av pyproject.toml uv.lock .python-version ユーザー名@サーバー:~/blog/
   rsync -av --exclude '__pycache__' --exclude 'instance/*.db' \
     --include 'static/uploads/.htaccess' --exclude 'static/uploads/*' \
     src/ ユーザー名@サーバー:<管理画面に表示された公開フォルダ>/
   ```

3. サーバー（SSH）で環境を作る

   ```bash
   cd ~/blog
   uv sync --frozen --python 3.10
   ```

4. `index.cgi` の1行目 `USERNAME` を実際のユーザー名に書き換える
5. 権限設定（CGI の実行ユーザーが書き込める必要があります）

   ```bash
   cd <公開フォルダ>
   chmod 755 index.cgi instance static/uploads
   ```

6. SECRET_KEY を設定（**本番は必須**。どちらか）
   - `.htaccess` の `SetEnv SECRET_KEY ...` のコメントを外して値を設定
   - `instance/secret_key.txt` にランダムな文字列を1行で保存
7. 管理者ユーザーを作成

   ```bash
   cd <公開フォルダ>
   APP_ENV=production ~/blog/.venv/bin/python create_admin.py 好きなユーザーID
   ```

8. SSH上でCGIを手動実行して確認

   ```bash
   REQUEST_METHOD=GET PATH_INFO=/ SCRIPT_NAME=/index.cgi \
   SERVER_NAME=localhost SERVER_PORT=80 HTTP_HOST=localhost \
   ./index.cgi | head -20
   ```

   `Status: 200 OK` に続いてHTMLが出れば成功です。

9. HTTPS で運用する場合は `.htaccess` の `SetEnv SESSION_COOKIE_SECURE 1` を有効化

### つまずきやすい点

- 500エラー: 管理画面のエラーログを確認。`index.cgi` が CRLF になっていないか確認
- `bad interpreter`: シバンのパス違い、または `.venv` が指す Python を CGI 実行ユーザーが読めない
- `SECRET_KEY が未設定です`: 手順6を実施
- ログインできない（HTTPのまま）: `SESSION_COOKIE_SECURE` を有効にしていないか確認
- 管理画面で対象ドメインの CGI が有効か確認
- SQLite に書けない / 画像を保存できない: `instance/` と `static/uploads/` の権限・所有者を確認
- CGI では `print` を使わない（HTTPレスポンスに混ざる）

## メモ

- 記事の取得は `db.get_or_404(Post, id)` を使用（Flask-SQLAlchemy 3 の API。`db.session.get_or_404` というメソッドは存在しません）。
- 日時は `datetime.now`（サーバーのローカル時刻）で保存します。

```console
[hanacore@s97 blogpro]$ APP_ENV=production ~/public_html/hanamaru8700.com/uvblog/.venv/bin/python create_admin.py hanaadgm
in.py hanaadgm
パスワード:
パスワード（確認）:
hanaka_taiyou_blog
管理者ユーザー「hanaadgm」を作成しました。
[hanacore@s97 blogpro]$
```
