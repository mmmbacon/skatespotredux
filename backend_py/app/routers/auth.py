from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from jose import jwt
from datetime import datetime, timedelta
from .config import get_settings

router = APIRouter(prefix="/auth/google", tags=["auth"])

settings = get_settings()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="google_callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="OAuth failed") from exc

    user_info = token.get("userinfo") or token["id_token_claims"]

    # TODO: upsert user in database

    payload = {
        "sub": user_info["sub"],
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    app_jwt = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    response = JSONResponse({"token": app_jwt})
    response.set_cookie(
        key="access_token",
        value=app_jwt,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response 