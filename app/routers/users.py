from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from .. import jwt
from ..dependencies import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("", response_model=list[schemas.User])
def read_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
    current_user: schemas.UserSchema = Depends(jwt.get_current_active_user)
):
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserSchema)
async def read_users_me(current_user: schemas.UserSchema = Depends(jwt.get_current_active_user)):
    return current_user
