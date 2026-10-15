"""Two seeded demo accounts, verified server-side with PBKDF2 and signed cookies.

No credentials or role claims are trusted from the browser. No Supabase schema
or existing business Use Case is changed by this authentication layer.
"""
import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"], include_in_schema=False)
SESSION_COOKIE = "rtsync_auth_session"
SESSION_SECONDS = 8 * 60 * 60
ACCOUNTS = {"rtsync1": ("owner", "rtsync_owner_password_hash"),
            "rtsync3": ("employee", "rtsync_employee_password_hash")}


class LoginInput(BaseModel):
    username: str
    password: str


def _encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _hash_matches(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
        computed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), 310000
        )
        return hmac.compare_digest(computed, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False


def _secret() -> bytes:
    value = settings.rtsync_session_secret
    if len(value) < 32:
        raise HTTPException(status_code=503, detail="Authentication not configured")
    return value.encode("utf-8")


def _session_token(username: str) -> str:
    payload = {"sub": username, "exp": int(time.time()) + SESSION_SECONDS}
    encoded = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _encode(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
    return f"{encoded}.{signature}"


async def authorized_user(token: str | None):
    if not settings.rtsync_auth_required:
        raise HTTPException(status_code=503, detail="Authentication not enabled")
    if not token:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")
    try:
        encoded, signature = token.split(".", 1)
        expected = _encode(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        payload = json.loads(_decode(encoded))
        username = payload["sub"]
        if type(payload["exp"]) is not int or payload["exp"] <= int(time.time()):
            raise ValueError("expired")
        role, attr = ACCOUNTS[username]
        if not getattr(settings, attr):
            raise ValueError("disabled")
    except (KeyError, ValueError, TypeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่") from None
    return {"id": username, "name": username, "username": username, "role": role}


@router.get("/status")
async def status():
    return JSONResponse({"enabled": bool(settings.rtsync_auth_required), "roles": ["owner", "employee"]},
                        headers={"Cache-Control": "no-store"})


@router.post("/login")
async def login(request: Request, payload: LoginInput):
    if not settings.rtsync_auth_required:
        raise HTTPException(status_code=503, detail="Login is not enabled")
    user = payload.username.strip().lower()
    account = ACCOUNTS.get(user)
    # Uniform failure response; password hashes are server-only environment variables.
    if not account:
        hashlib.pbkdf2_hmac("sha256", payload.password.encode(), b"unknown-user-salt", 310000)
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    role, attr = account
    password_hash = getattr(settings, attr)
    if not password_hash or not _hash_matches(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    result = JSONResponse({"username": user, "name": user, "role": role},
                          headers={"Cache-Control": "no-store"})
    result.set_cookie(SESSION_COOKIE, _session_token(user), httponly=True,
                      secure=settings.app_env == "production", samesite="strict",
                      max_age=SESSION_SECONDS, path=settings.api_prefix.rstrip("/"))
    return result


@router.get("/me")
async def me(request: Request):
    return JSONResponse(await authorized_user(request.cookies.get(SESSION_COOKIE)),
                        headers={"Cache-Control": "no-store"})


@router.post("/logout")
async def logout():
    response = JSONResponse({"status": "signed_out"}, headers={"Cache-Control": "no-store"})
    response.delete_cookie(SESSION_COOKIE, path=settings.api_prefix.rstrip("/"))
    return response
