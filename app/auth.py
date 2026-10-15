"""Server-side Google OAuth via Supabase Auth.

No Supabase publishable key or Postgres credentials are sent to the browser.
All business API access requires a verified Google account on the allowlist
when RTSYNC_AUTH_REQUIRED is enabled.
"""
import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"], include_in_schema=False)

SESSION_COOKIE = "rtsync_auth_session"
VERIFIER_COOKIE = "rtsync_oauth_verifier"
STATE_COOKIE = "rtsync_oauth_state"


def _enabled():
    return bool(settings.rtsync_auth_required)


def _auth_base():
    return settings.supabase_auth_url.rstrip("/") + "/auth/v1"


def _headers(access_token=None):
    headers = {"apikey": settings.supabase_auth_key}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _secure_cookies():
    return settings.app_env.lower() == "production"


def _is_allowed(user):
    email = (user.get("email") or "").strip().casefold()
    allowed = {item.strip().casefold() for item in settings.rtsync_allowed_emails.split(",") if item.strip()}
    providers = user.get("app_metadata", {}).get("providers", [])
    if not providers:
        providers = [user.get("app_metadata", {}).get("provider")]
    return bool(email and user.get("email_confirmed_at") and email in allowed and "google" in providers)


async def authorized_user(token):
    """Verify the bearer token with Supabase, then enforce the email allowlist."""
    if not token or not settings.supabase_auth_key:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบด้วย Google")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(f"{_auth_base()}/user", headers=_headers(token))
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="ไม่สามารถตรวจสอบบัญชีผู้ใช้ได้") from None
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่")
    user = response.json()
    if not _is_allowed(user):
        raise HTTPException(status_code=403, detail="บัญชี Google นี้ยังไม่ได้รับอนุญาตให้ใช้ RTSync")
    return {"id": user.get("id"), "name": user.get("user_metadata", {}).get("full_name") or user.get("email"), "email": user.get("email")}


def _login_redirect(error):
    return RedirectResponse(url=f"/login?{urlencode({'error': error})}", status_code=303)


@router.get("/google")
async def login_google():
    if not _enabled() or not settings.supabase_auth_key or not settings.rtsync_allowed_emails.strip():
        raise HTTPException(status_code=503, detail="Google Login ยังไม่ได้เปิดใช้งาน")
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    redirect_to = settings.frontend_origin.rstrip("/") + settings.api_prefix + "/auth/callback"
    authorization_url = f"{_auth_base()}/authorize?" + urlencode({
        "provider": "google",
        "redirect_to": redirect_to,
        "code_challenge": challenge,
        "code_challenge_method": "s256",
        "state": state,
    })
    response = RedirectResponse(authorization_url, status_code=303)
    for key, value in [(VERIFIER_COOKIE, verifier), (STATE_COOKIE, state)]:
        response.set_cookie(key, value, httponly=True, secure=_secure_cookies(), samesite="lax", max_age=600, path=settings.api_prefix + "/auth")
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/callback")
async def google_callback(request: Request, code: str | None = None, state: str | None = None):
    verifier = request.cookies.get(VERIFIER_COOKIE)
    original_state = request.cookies.get(STATE_COOKIE)
    if not verifier or not state or not original_state or not secrets.compare_digest(state, original_state) or not code:
        return _login_redirect("oauth")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            exchange = await client.post(
                f"{_auth_base()}/token?grant_type=pkce",
                json={"auth_code": code, "code_verifier": verifier},
                headers=_headers(),
            )
        if exchange.status_code != 200:
            return _login_redirect("oauth")
        token = exchange.json().get("access_token")
        await authorized_user(token)
    except (httpx.HTTPError, HTTPException, ValueError):
        return _login_redirect("not_approved")
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE, token, httponly=True, secure=_secure_cookies(),
        samesite="strict", max_age=min(max(int(exchange.json().get("expires_in", 3600)) - 30, 60), 3600),
        path=settings.api_prefix,
    )
    response.headers["Cache-Control"] = "no-store"
    for key in (VERIFIER_COOKIE, STATE_COOKIE):
        response.delete_cookie(key, path=settings.api_prefix + "/auth")
    return response


@router.get("/me")
async def me(request: Request):
    if not _enabled():
        raise HTTPException(status_code=404, detail="Authentication is not enabled")
    user = await authorized_user(request.cookies.get(SESSION_COOKIE))
    return JSONResponse(user, headers={"Cache-Control": "no-store"})


@router.post("/logout")
async def logout():
    response = JSONResponse({"status": "signed_out"}, headers={"Cache-Control": "no-store"})
    response.delete_cookie(SESSION_COOKIE, path=settings.api_prefix)
    return response
