from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from jose import jwt
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..config import get_settings
from ..database import get_db
from ..models.user import User

router = APIRouter(prefix="/auth/google", tags=["auth"])

settings = get_settings()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# OAuth2 bearer for JWT issued by our backend
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google/login")


@router.get("/login")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="OAuth failed") from exc

    user_info = token.get("userinfo") or token["id_token_claims"]

    # --- upsert user in database ------------------------------------------
    stmt = select(User).where(User.email == user_info.get("email"))
    result = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user:
        user.name = user_info.get("name")
        user.picture = user_info.get("picture")
        user.last_login = datetime.utcnow()
    else:
        user = User(
            email=user_info.get("email"),
            name=user_info.get("name"),
            picture=user_info.get("picture"),
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    payload = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    app_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    frontend_redirect_url = "http://localhost:5173/auth/success?token=" + app_jwt

    response = RedirectResponse(url=frontend_redirect_url, status_code=status.HTTP_302_FOUND)
    # Store token in an HTTP-only cookie (optional but recommended)
    response.set_cookie(
        key="access_token",
        value=app_jwt,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=12 * 60 * 60,  # 12 hours
    )
    return response


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Validate JWT from Authorization header and return the corresponding user."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_uuid = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user: User | None = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat(),
    } 