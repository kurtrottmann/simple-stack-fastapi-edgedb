from datetime import timedelta
from typing import Any

from edgedb import AsyncIOConnection
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, db, schemas
from app.config import settings
from app.security import (
    create_access_token,
    generate_password_reset_token,
    get_password_hash,
    verify_password_reset_token,
)
from app.utils import send_reset_password_email

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    con: AsyncIOConnection = Depends(db.get_con),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        con, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = schemas.Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires),
        token_type="bearer",
    )
    return token


@router.post("/login/test-token", response_model=schemas.User)
async def test_token(
    current_user: schemas.User = Depends(auth.get_current_user),
) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
async def recover_password(
    email: str, con: AsyncIOConnection = Depends(db.get_con)
) -> Any:
    """
    Password Recovery
    """
    user = await crud.user.get_by_email(con, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    msg = schemas.Msg(msg="Password recovery email sent")
    return msg


@router.post("/reset-password/", response_model=schemas.Msg)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    con: AsyncIOConnection = Depends(db.get_con),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.user.get_by_email(con, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user_in = schemas.UserUpdate(hashed_password=hashed_password)
    await crud.user.update(con, id=user.id, obj_in=user_in)
    msg = schemas.Msg(msg="Password updated successfully")
    return msg
