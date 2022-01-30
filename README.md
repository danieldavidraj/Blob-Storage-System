# Blob Storage System

---

**Heroku Deployment Link**: <a href="https://blob-storage-system.herokuapp.com" target="_blank">Blob Storage System</a>

**Video Link**: <a href="https://drive.google.com/file/d/11MFr6Ak-YDwWyU3sGQNvewX-mKkmSWmG/view?usp=sharing" target="_blank">Demo</a>

---

A Simple Blog Storage System for storing files where users can view, upload, rename, delete, share, download and compress files with user based access control on who can access the files.

The key features are:

* **Admin access**: Admin access for viewing users and their uploaded files and deleting users and files.
* **Authentication**: Authentication using OAuth2 with Password (and hashing), Bearer with JWT tokens.
* **Authorization**: Authorization using OAuth2 scopes.
* **Access control**: User based access control on who can access the files, rename and delete.
* **Compress Files**: Can compress into zip and download files.
* **Storage**: The files are stored in the 'static' folder with name in the format "<user_id>_<unix_timestamp>" because a user with a user id can never upload two files at the same time and the path of the file is stored in the database.


## Requirements

Python 3.6+

## Installation

```console
$ git clone https://github.com/danieldavidraj/Blob-Storage-System.git

---> 100%
```
```console
$ cd Blob-Storage-System
```
```console
$ pip install -r requirements.txt

---> 100%
```
```console
$ uvicorn app.main:app --host 0.0.0.0 --port 80
```
Go to the <a href="http://localhost" target="_blank">link</a> to see the application