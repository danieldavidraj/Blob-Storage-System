import re
import mimetypes
import requests
from os.path import exists as file_exists
from requests.exceptions import HTTPError

base_url = "http://localhost:8000"

session = requests.Session()

def user_logged_in():
    response = session.get(f"{base_url}/loggedin")
    if response.status_code == 200:
        return True
    return False

def get_session():
    try:
        response = session.get(f"{base_url}/loggedin")
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.text)
    else:
        return response.json()['token']

def create_session(token):
    try:
        payload = {'token': token}
        response = session.post(f"{base_url}/create_session", json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        print(http_err)

def get_token(username, password):
    payload = {'username': username, 'password': password}
    try:
        response = session.post(f"{base_url}/token", data=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        return response.json()['token_type'] + " " + response.json()['access_token']

def Login():
    username = input("Username: ")
    password = input("Password: ")
    token = get_token(username, password)
    if token:
        print("\nSuccessfully logged in")
        create_session(token)
        return token

def Register():
    username = input("Username: ")
    password = input("Password: ")
    payload = {'username': username, 'password': password}
    try:    
        response = session.post(f"{base_url}/users/", json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("\nSuccessfully registered")
        token = get_token(username, password)
        create_session(token)
        return token

def Authentication():
    while True:   
        if user_logged_in():
            print("User already logged in")
            return get_session()
        else:
            print("1) Login")
            print("2) Register")
            try:
                choice = int(input("Choice: "))
                if choice == 1:
                    token = Login()
                    if token:
                        return token
                elif choice == 2:
                    token = Register()
                    if token:
                        return token
                else:
                    print("Invalid entry")
            except ValueError as ve:
                print("Enter an integer")

def display_files(files):
    sno = 1
    for file in files:
        print(f"{sno})")
        print(f"Id: {file['id']}")
        print(f"Name: {file['title']}")
        print(f"Description: {file['description']}")
        sno += 1

def display_users(users):
    sno = 1
    for user in users:
        print(f"{sno})")
        print(f"Id: {user['id']}")
        print(f"Username: {user['username']}")
        sno += 1

def view_file(id):
    file_id = input("Enter the id of the file to view: ")
    try:    
        response = session.get(f"{base_url}/users/{id}/files/{file_id}")
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        file = response.json()
        print(f"Id: {file['id']}")
        print(f"Name: {file['title']}")
        print(f"Description: {file['description']}")
        
def upload_file(id):
    try: 
        file_name = input("Enter the file name: ")
        if file_exists(file_name):
            content_type = mimetypes.guess_type(file_name)
            files = {'uploadfile': (file_name, open(file_name, 'rb'), content_type[0])}
            response = session.post(f"{base_url}/users/{id}/files", files=files)
            response.raise_for_status()
        else:
            print("File not found")
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("Successfully uploaded")  

def edit_file(id):
    file_id = input("Enter the id of the file to edit: ")
    print("Enter to change or leave empty to remain as it is!")
    title = input("Enter the name of the file: ")
    description = input("Enter the description of the file: ")
    data = {'title': title, 'description': description}
    try:    
        response = session.put(f"{base_url}/users/{id}/files/{file_id}", json=data)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("Successfully edited")

def delete_file(id):
    file_id = input("Enter the id of the file to delete: ")
    try:    
        response = session.delete(f"{base_url}/users/{id}/files/{file_id}")
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("Successfully deleted")

def share_file(id):
    file_id = input("Enter the id of the file to share: ")
    response = session.get(f"{base_url}/users/")
    display_users(response.json())
    username = input("Enter the username of the user to share: ")
    data = {'username': username}
    try: 
        response = session.patch(f"{base_url}/users/{id}/files/{file_id}/share", json=data)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("Successfully shared")   

def download_file(id):
    file_id = input("Enter the id of the file to download: ")
    try: 
        response = session.get(f"{base_url}/users/{id}/files/{file_id}/download", allow_redirects=True)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        content_type = response.headers.get('content-type')
        extension = content_type.split("/")[-1]
        if 'plain' in extension:
            extension = 'txt'
        cd = response.headers.get('content-disposition')
        fname = re.findall("filename=(.+)", cd)
        if not fname:
            fname = re.findall("utf-8''(.+)", cd)
        fname = fname[0].replace('"', '').replace('%20', ' ')
        if extension not in fname:
            fname += '.' + extension
        open(fname, 'wb').write(response.content)
        print("Successfully downloaded")   

def compress_file(id):
    file_id = input("Enter the id of the file to compress: ")
    try: 
        response = session.get(f"{base_url}/users/{id}/files/{file_id}/compress", allow_redirects=True)
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        cd = response.headers.get('content-disposition')
        fname = re.findall("filename=(.+)", cd)
        if not fname:
            fname = re.findall("utf-8''(.+)", cd)
        fname = fname[0].replace('"', '').replace('%20', ' ')
        open(fname, 'wb').write(response.content)
        print("Successfully compressed and downloaded")   

def logout():
    try: 
        response = session.post(f"{base_url}/logout")
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        print("Successfully logged out")   
        return True

def Menu(id):
    while True:
        response = session.get(f"{base_url}/users/{id}/files")
        
        print("\nOwn Files: ")
        own_files = response.json()['own_files']
        if own_files:
            display_files(own_files)
        else:
            print("No files owned")

        print("\nShared Files: ")
        shared_files = response.json()['shared_files']
        if shared_files:
            display_files(shared_files)
        else:
            print("No files shared")

        print("\n1) View file")
        print("2) Upload file")
        print("3) Rename file")
        print("4) Delete file")
        print("5) Share file")
        print("6) Download file")
        print("7) Compress file")
        print("8) Logout")

        try:
            choice = int(input("Choice: "))

            if choice == 1:
                view_file(id)
            
            elif choice == 2:
                upload_file(id)  

            elif choice == 3:
                edit_file(id)

            elif choice == 4:
                delete_file(id)
                
            elif choice == 5:
                share_file(id)
            
            elif choice == 6:
                download_file(id)
            
            elif choice == 7:
                compress_file(id)
            
            elif choice == 8:
                if logout():
                    break
            else:
                print("Invalid entry")
            
        except ValueError as ve:
            print("Enter an integer")


if __name__=="__main__":
    print("Simple Blob Storage System\n")

    token = Authentication()
    
    session.headers.update({
        "accept": "application/json",
        "Authorization": token
    })
    
    try: 
        response = session.get(f"{base_url}/users/me/")
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.json()['detail'])
    else:
        id = response.json()['id']
        print(f"Username: {response.json()['username']}")

        Menu(id)

    
        

            
            







    







