from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

# scrypt が使えない環境でも動くよう pbkdf2 を明示
PASSWORD_HASH_METHOD = "pbkdf2:sha256"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)  # 削除フラグ
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)  # 登録日
    updated_at = db.Column(  # 更新日（変更時に自動で書き換わる）
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(
            raw_password, method=PASSWORD_HASH_METHOD
        )

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)
