from __future__ import annotations

import hashlib
import os
import sqlite3
from typing import Optional

from database import get_connection


def user_exists() -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()
        return row["total"] > 0


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, salt FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        return row


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )


def create_user(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()

    if not email:
        return False, "Informe um e-mail."
    if "@" not in email:
        return False, "Informe um e-mail válido."
    if len(password) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."

    if get_user_by_email(email) is not None:
        return False, "Este e-mail já está cadastrado."

    salt = os.urandom(16)
    password_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (email, password_hash, salt)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, salt),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Este e-mail já está cadastrado."

    return True, "Usuário criado com sucesso."


def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    row = get_user_by_email(email)

    if row is None:
        return False, "E-mail ou senha inválidos."

    expected_hash = row["password_hash"]
    salt = row["salt"]
    informed_hash = hash_password(password, salt)

    if informed_hash != expected_hash:
        return False, "E-mail ou senha inválidos."

    return True, "Login realizado com sucesso."


def update_password(
    email: str,
    current_password: str,
    new_password: str,
) -> tuple[bool, str]:
    email = email.strip().lower()

    ok, _ = authenticate_user(email, current_password)
    if not ok:
        return False, "A senha atual está incorreta."

    if len(new_password) < 6:
        return False, "A nova senha deve ter pelo menos 6 caracteres."

    new_salt = os.urandom(16)
    new_hash = hash_password(new_password, new_salt)

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, salt = ?
            WHERE email = ?
            """,
            (new_hash, new_salt, email),
        )
        conn.commit()

    return True, "Senha alterada com sucesso."