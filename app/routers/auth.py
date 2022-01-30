from fastapi import APIRouter, Depends, HTTPException, Response
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from functools import lru_cache
from uuid import UUID, uuid4

from .. import config
from .. import schemas
from .. import jwt
from ..dependencies import get_db
from ..sessions import cookie, backend, verifier

@lru_cache()
def get_settings():
    return config.Settings()

router = APIRouter(
    prefix="",
    tags=["authentication"]
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db), 
    settings: config.Settings = Depends(get_settings)
):
    user = jwt.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    print(user.is_admin)
    if user.is_admin:
        scopes=['admin']
    else:
        scopes=['user']    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = jwt.create_access_token(
        settings, 
        data={"sub": user.username, "scopes": scopes}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create_session")
async def create_session(session_token: schemas.SessionData, response: Response):
    session = uuid4()
    data = schemas.SessionData(token=session_token.token)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {session_token.token}"

@router.get("/loggedin", dependencies=[Depends(cookie)])
async def logged_in(session_data: schemas.SessionData = Depends(verifier)):
    return session_data

@router.post("/logout")
async def log_out(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"