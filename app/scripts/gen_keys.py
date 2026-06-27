# app/scripts/gen_keys.py
"""Генерация пары RSA-ключей для подписи JWT (RS256).

Использование:
    python -m app.scripts.gen_keys

Пишет приватный и публичный ключи в каталог keys/ (он в .gitignore).
Приватный ключ держим в секрете и НЕ коммитим. На проде раздаём через
секрет-хранилище (KMS/Vault), а не файлом в репозитории.
"""
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings


def main() -> None:
    priv_path = Path(settings.JWT_PRIVATE_KEY_PATH)
    pub_path = Path(settings.JWT_PUBLIC_KEY_PATH)
    priv_path.parent.mkdir(parents=True, exist_ok=True)

    if priv_path.exists() or pub_path.exists():
        raise SystemExit(
            f"Ключи уже существуют ({priv_path} / {pub_path}). "
            "Удалите их вручную, если действительно нужна ротация."
        )

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_path.write_bytes(priv_pem)
    pub_path.write_bytes(pub_pem)
    # Приватный ключ — только владельцу
    priv_path.chmod(0o600)

    print(f"Приватный ключ: {priv_path}")
    print(f"Публичный ключ: {pub_path}")


if __name__ == "__main__":
    main()
