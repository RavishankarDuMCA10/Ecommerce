from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

APP_TITLE = "CTT Auth Service"
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DB_PATH = Path(__file__).resolve().parent / "auth.db"
TOKEN_TTL_HOURS = 12
REMEMBER_ME_DAYS = 14

app = FastAPI(title=APP_TITLE, version="0.1.0")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                gender TEXT NOT NULL,
                mobile TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=128)
    gender: str = Field(min_length=1, max_length=20)
    mobile: str = Field(min_length=8, max_length=20)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    remember_me: bool = False


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    gender: Optional[str] = Field(default=None, min_length=1, max_length=20)
    mobile: Optional[str] = Field(default=None, min_length=8, max_length=20)


class AuthResponse(BaseModel):
    token: str
    expires_at: str
    user: dict


def hash_password(password: str, salt_b64: str) -> str:
    salt = base64.b64decode(salt_b64.encode("utf-8"))
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return base64.b64encode(hashed).decode("utf-8")


def make_salt() -> str:
    return base64.b64encode(os.urandom(16)).decode("utf-8")


def validate_email(email: str) -> None:
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Email must be in abc@xyz.com format")


def normalize_bearer(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Authorization header must be Bearer token")
    token = authorization[len(prefix) :].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return token


def user_from_token(authorization: Optional[str]) -> sqlite3.Row:
    token = normalize_bearer(authorization)
    with get_conn() as conn:
        session = conn.execute(
            "SELECT token, user_id, expires_at FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=401, detail="Session not found")

        expires_at = datetime.fromisoformat(session["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            raise HTTPException(status_code=401, detail="Session expired")

        user = conn.execute(
            "SELECT id, name, email, gender, mobile, created_at, updated_at FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()
        if not user:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            raise HTTPException(status_code=401, detail="User not found")
        return user


@app.get("/health")
def health() -> dict:
    return {"service": "auth", "status": "ok"}


@app.post("/auth/register")
def register(payload: RegisterRequest) -> dict:
    validate_email(payload.email)
    now = datetime.now(timezone.utc).isoformat()
    salt = make_salt()
    password_hash = hash_password(payload.password, salt)

    with get_conn() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (payload.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        cursor = conn.execute(
            """
            INSERT INTO users(name, email, gender, mobile, password_hash, password_salt, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                payload.email.strip().lower(),
                payload.gender.strip(),
                payload.mobile.strip(),
                password_hash,
                salt,
                now,
                now,
            ),
        )
        user_id = cursor.lastrowid

    return {"message": "Registration successful", "user_id": user_id}


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    validate_email(payload.email)

    with get_conn() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (payload.email.strip().lower(),)
        ).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        incoming_hash = hash_password(payload.password, user["password_salt"])
        if not secrets.compare_digest(incoming_hash, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = secrets.token_urlsafe(36)
        now = datetime.now(timezone.utc)
        ttl = timedelta(days=REMEMBER_ME_DAYS) if payload.remember_me else timedelta(hours=TOKEN_TTL_HOURS)
        expires_at = (now + ttl).isoformat()

        conn.execute(
            "INSERT INTO sessions(token, user_id, expires_at, created_at) VALUES(?, ?, ?, ?)",
            (token, user["id"], expires_at, now.isoformat()),
        )

    user_payload = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "gender": user["gender"],
        "mobile": user["mobile"],
    }

    return AuthResponse(token=token, expires_at=expires_at, user=user_payload)


@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)) -> dict:
    token = normalize_bearer(authorization)
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    return {"message": "Logout successful"}


@app.get("/auth/profile")
def get_profile(authorization: Optional[str] = Header(default=None)) -> dict:
    user = user_from_token(authorization)
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "gender": user["gender"],
        "mobile": user["mobile"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


@app.put("/auth/profile")
def update_profile(payload: ProfileUpdateRequest, authorization: Optional[str] = Header(default=None)) -> dict:
    user = user_from_token(authorization)

    updates: dict[str, str] = {}
    if payload.name is not None:
        updates["name"] = payload.name.strip()
    if payload.gender is not None:
        updates["gender"] = payload.gender.strip()
    if payload.mobile is not None:
        updates["mobile"] = payload.mobile.strip()

    if not updates:
        raise HTTPException(status_code=400, detail="No profile fields provided")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values())
    values.append(user["id"])

    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)

    return {"message": "Profile updated successfully"}
