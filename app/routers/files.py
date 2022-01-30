import os
import time
import shutil
import zipfile
from os.path import exists as file_exists
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from .. import crud, schemas
from ..dependencies import (
    verify_user, 
    verify_owner, 
    get_db, 
    have_permission_rename, 
    have_permission_delete, 
    verify_other_user, 
    have_permission_view
)

router = APIRouter(
    prefix="/users/{user_id}",
    tags=["files"],
    dependencies=[Depends(verify_user)],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/files", response_model=schemas.FileSchema
)
def view_files(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.view_files(db, user_id=user_id, skip=skip, limit=limit)

@router.post(
    "/files", response_model=schemas.File
)
def upload_file(user_id: int, uploadfile: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = uploadfile.content_type.split("/")[1]
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(path, os.pardir)) + "\\static\\" + str(user_id) + "_" + str(int(time.time())) + "." + extension
    with open(path, "wb") as buffer:
        shutil.copyfileobj(uploadfile.file, buffer)

    return crud.upload_file(db=db, title=uploadfile.filename, path=path, type=uploadfile.content_type, user_id=user_id)

@router.get(
    "/files/{file_id}", response_model=schemas.File,
    dependencies=[Depends(have_permission_view)]
)
def view_file(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.put(
    "/files/{file_id}", response_model=schemas.File, 
    dependencies=[Depends(have_permission_rename)]
)
def rename_file(file_id: int, file: schemas.FileBase, db: Session = Depends(get_db)):
    return crud.rename_file(db, file_id=file_id, file=file)

@router.delete(
    "/files/{file_id}", 
    dependencies=[Depends(have_permission_delete)]
)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id)
    response = crud.delete_file(db, file_id=file_id)
    os.remove(file.path)
    return response

@router.patch(
    "/files/{file_id}/share",
    dependencies=[Depends(verify_owner), Depends(verify_other_user)]
)
def share_file(file_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    return crud.share_file(db, file_id=file_id, username=user.username)

@router.get(
    "/files/{file_id}/download",
    dependencies=[Depends(have_permission_view)]
)
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file_exists(file.path):
        return FileResponse(file.path, media_type=file.type, filename=file.title)
    else:
        raise HTTPException(status_code=404, detail="File path not found")

@router.get(
    "/files/{file_id}/compress",
    dependencies=[Depends(have_permission_view)]
)
def compress_file(file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    compression = zipfile.ZIP_DEFLATED
    zip_file_name = file.path + ".zip"
    zf = zipfile.ZipFile(zip_file_name, mode="w")
    try:
        extension = file.type.split("/")[1]
        if 'plain' in extension:
            extension = 'txt'
        if extension not in file.title:
            file_title_extension = f"{file.title}.{extension}"
            file_title_without_extension = file.title
        else:
            file_title_extension = file.title
            file_title_without_extension = file.title.replace(f'.{extension}', '')
        zf.write(file.path, file_title_extension, compress_type=compression)
    except FileNotFoundError as e:
        print(f'Exception occurred during zip process - {e}')
    finally:
        zf.close()    
    return FileResponse(zip_file_name, media_type='application/zip', filename=file_title_without_extension + ".zip")