from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import jwt, models, schemas
from fastapi import HTTPException

# User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = jwt.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def enable_disable_user(db: Session, user_id: int, disable: bool):
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    setattr(db_user, "disabled", disable)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# File
def get_file(db: Session, file_id: int):
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()

def upload_file(db: Session, title: str, path: str, type: str, user_id: int):
    db_file = models.File(title=title, path=path, type=type, owner_id=user_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    create_permission(db, user_id, db_file.id)
    return db_file

def view_files(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    permissions = db.query(models.Permission)\
            .filter(and_(models.Permission.user_id == user_id, models.Permission.view==True))\
            .offset(skip)\
            .limit(limit)\
            .all()
    own_files = []
    shared_files = []
    for permission in permissions:
        file = db.query(models.File).filter(models.File.id == permission.file_id).one_or_none()
        if file.owner_id == user_id:
            own_files.append(file)
        else:
            shared_files.append(file)
    return {'own_files': own_files, 'shared_files': shared_files}

def rename_file(db: Session, file_id: int, file: schemas.FileBase):
    db_file = db.get(models.File, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if file.title:
        setattr(db_file, "title", file.title)
    if file.description:
        setattr(db_file, "description", file.description)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def delete_file(db: Session, file_id: int):
    remove_permission(db, file_id=file_id)
    db_file = db.get(models.File, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()
    return {"ok": True}

def share_file(db: Session, file_id: int, username: str):
    user = get_user_by_username(db, username)
    db_perm = get_permission(db, file_id, user.id)        
    if db_perm:
        set_read_permission(db, db_perm)
    else:
        create_read_permission(db, user.id, file_id)
    return {'detail': 'Successfully shared'}

# Permission
def get_permission(db: Session, user_id: int, file_id: int):
    return db.query(models.Permission)\
            .filter(and_(models.Permission.file_id == file_id, models.Permission.user_id == user_id))\
            .one_or_none()   

def set_read_permission(db, db_perm: schemas.Perm):
    setattr(db_perm, "view", True)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

def create_read_permission(db, user_id: int, file_id: int):
    db_perm = models.Permission(user_id=user_id, file_id=file_id, view=True, rename=False, delete=False)
    db.add(db_perm)
    db.commit() 
    return db_perm

def create_permission(db: Session, user_id: int, file_id: int):
    db_perm = models.Permission(user_id=user_id, file_id=file_id, view=True, rename=True, delete=True)
    db.add(db_perm)
    db.commit()

def remove_permission(db: Session, file_id: int):
    db_files = db.query(models.Permission).filter(models.Permission.file_id == file_id).all()
    for file in db_files:
        delete_file = db.get(models.Permission, file.id)
        db.delete(delete_file)
    db.commit()

