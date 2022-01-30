from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import crud, jwt, schemas

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_user(user_id: int, current_user: schemas.User = Depends(jwt.get_current_active_user)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )

async def verify_owner(user_id: int, file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if user_id != file.owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )

async def have_permission_rename(user_id: int, file_id: int, db: Session = Depends(get_db)):
    perm = crud.get_permission(db, user_id, file_id)
    if not perm:
        raise HTTPException(status_code=404, detail="File not found")
    if perm.rename != True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )

async def have_permission_delete(user_id: int, file_id: int, db: Session = Depends(get_db)):
    perm = crud.get_permission(db, user_id, file_id)
    if not perm:
        raise HTTPException(status_code=404, detail="File not found")
    if perm.delete != True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )

async def verify_other_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Can only share with other users"
        )