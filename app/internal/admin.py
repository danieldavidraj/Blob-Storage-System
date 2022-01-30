import os
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from .. import crud, schemas, jwt
from ..dependencies import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/users", response_model=list[schemas.UserSchema])
def read_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    return crud.get_users(db, skip=skip, limit=limit)
    
@router.get("/users/{user_id}", response_model=schemas.UserSchema)
def read_user(
    user_id: int, db: Session = Depends(get_db), 
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/files", response_model=list[schemas.File])
def read_files(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    return crud.get_files(db, skip=skip, limit=limit)

@router.get("/files/{file_id}", response_model=schemas.File)
def read_file(
    file_id: int, db: Session = Depends(get_db), 
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    db_file = crud.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.patch("/users/{user_id}/enable", response_model=schemas.UserSchema)
def enable_user(
    user_id: int, db: Session = Depends(get_db), 
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    return crud.enable_disable_user(db, user_id=user_id, disable=False)

@router.patch("/users/{user_id}/disable", response_model=schemas.UserSchema)
def disable_user(
    user_id: int, db: Session = Depends(get_db),
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    return crud.enable_disable_user(db, user_id=user_id, disable=True)

@router.delete("/files/{file_id}")
def delete_file(
    file_id: int, db: Session = Depends(get_db), 
    current_user: schemas.User = Security(jwt.get_current_user, scopes=["admin"])
):
    file = crud.get_file(db, file_id)
    response = crud.delete_file(db, file_id=file_id)
    os.remove(file.path)
    return response



