import contextlib
import json
import sys
from random import choices
from pathlib import Path 
import os

import requests

root_url = os.environ.get("WEBSITE") or "http://127.0.0.1:5000"
create_bot_url = f"{root_url:s}/api/users"
tokens_url = f"{root_url:s}/api/tokens"
current_user_url = f"{root_url:s}/api/users/current"
all_the_messages_url = f"{root_url:s}/api/messages/all"
empty_messages_url = f"{root_url:s}/api/messages/empty"
publish_post_url = f"{root_url:s}/api/posts"
publish_picture_url = f"{root_url:s}/api/pictures"


store_path = Path("~", "Info", "athena", "webclient", "store").expanduser()
store_path.mkdir(mode=0o700, parents=True, exist_ok=True)

def create_bot(username, password):
    payload = {"username": username, "password": password}
    response = requests.post(create_bot_url, json=payload)
    return response

def login_bot(username, password):
    response = requests.post(tokens_url, auth=requests.auth.HTTPBasicAuth(username, password))
    return response

def get_token_headers(token):
    auth_headers = requests.structures.CaseInsensitiveDict()
    auth_headers["Accept"] = "application/json"
    auth_headers["Authorization"] = f"Bearer {token}"
    return auth_headers

def get_current_user(auth_headers):
    response = requests.get(current_user_url, headers=auth_headers)
    return response


# https://forpythons.com/how-to-upload-file-with-python-requests/

class WebClientException(Exception):
    pass

def get_filename_and_mimetype(image_file): 
    filename = image_file.name # todo    
    mimetype = ""
    parts = filename.split(".")
    try:
        extension = parts[1]
        if extension == "jpg" or extension == "jpeg":
            mimetype = "image/jpeg"
        elif extension == "png":
            mimetype = "image/png"
        else:
            raise WebClientException(f"Unexpected extension/mimetype {extension:s}")
    except IndexError:
        raise WebClientException(f"Skipping file {filename:s} with no extension. We dont guess mimetypes!")
    except ValueError as message:
        raise WebClientException(f"{str(message):s}")
    return filename, mimetype


def publish_post(auth_headers, content):
    payload = {"content": content}
    response = requests.post(publish_post_url, 
                             headers=auth_headers, 
                             json=payload)
    return response


def publish_picture(auth_headers, image_file, resource_uuid):
    filename, mimetype = get_filename_and_mimetype(image_file)
    print("publish_picture:", filename, " ", mimetype)
    payload = {
         "image": (filename, image_file, mimetype)
    }
    response = requests.post(f"{publish_picture_url:s}/{resource_uuid:s}", 
                             headers=auth_headers, 
                             files=payload)
    return response

    
def empty_data(file_identifier):
    custom_data = {"username": "", "password": "", "register": ""}
    with open(file_identifier, "w") as target:
         json.dump(custom_data, target)
    return custom_data

def load_data(file_identifier):
    try:
        with open(file_identifier, "r") as source:
            some_data = json.load(source)
    except FileNotFoundError:
        print(f"{str(file_identifier):s} not found!")
        some_data = empty_data(file_identifier)
    except json.decoder.JSONDecodeError:
        print(f"{str(file_identifier):s} bad json!")
        some_data = empty_data(file_identifier)
    return some_data

def write_data(some_data, file_identifier):
    with open(file_identifier, "w") as target:
         json.dump(some_data, target)

def report(response):
    status_code = response.status_code
    text = response.text
    print("status_code", status_code)
    print("*"*80)
    print(text)
    print("*"*80)                


def generate_secret_data(secret_data_file_identifier):
    randombot_data = load_data(secret_data_file_identifier)
    source = "abcdefghijklmnopqrstuvwxyz0123456789_()-+~"
    secret_data = {}
    secret_data["username"] = "".join(choices(source, k=10))
    secret_data["password"] = "".join(choices(source, k=10))
    secret_data["register"] = "yes"
    write_data(secret_data, secret_data_file_identifier)
    return secret_data

def get_secret_fields(secret_data):
    try:
        username, password, register = secret_data["username"], secret_data["password"], secret_data["register"]
    except KeyError as message:
        print("Error", str(message), "-", str(secret_data))
        username, password, register = "", "", ""
    return username, password, register


def get_all_the_messages(auth_headers):
    response = requests.get(all_the_messages_url, headers=auth_headers)
    return response


def clear_message_queue(auth_headers):
    response = requests.get(empty_messages_url, headers=auth_headers)
    return response


def get_auth_headers(username):
    if username == "random":
        username = "randombot"
        secret_data_file_identifier = Path(store_path, username + ".json")
        if secret_data_file_identifier.exists():
            secret_data = load_data(secret_data_file_identifier)
        else:
            secret_data = generate_secret_data(secret_data_file_identifier)
    else:
        secret_data_file_identifier = Path(store_path, username + ".json")
        if secret_data_file_identifier.exists():
            secret_data = load_data(secret_data_file_identifier)
        else:
            secret_data = generate_secret_data(secret_data_file_identifier)
            secret_data["username"] = username
            write_data(secret_data, secret_data_file_identifier)
    username, password, register = get_secret_fields(secret_data)
    auth_headers = None
    try:
        if len(username) == 0:
            raise ValueError("username unexpected null value")
        if len(password) == 0:
            raise ValueError("password unexpected null value")
        if  register == "yes":
            print("Register")
            response = create_bot(username, password)
            report(response)
            secret_data["user"] = response.json()
            secret_data["register"] = "no"
            write_data(secret_data, secret_data_file_identifier)
        elif register == "no":
            print("No need to register user")
        else:
            raise ValueError(f"register unexpected value {register:s}")
    except ValueError as message:
        print("Error", str(message))
    else:
        print("Getting authentication token")
        response = login_bot(username, password)
        report(response)
        if response.status_code == 200:
            print("Logged in")
            token_json = response.json()
            token = token_json["token"]
            print("Got the token", token)
            auth_headers = get_token_headers(token)
    return auth_headers

    
def get_messages(auth_headers):    
    if auth_headers:
        print("Get current user received messages")
        response = get_all_the_messages(auth_headers)
        as_json = response.json()
        items = as_json["items"]
        print("#"*80)
        print("messages")
        for message in items:
            yield message


def clear_messages(auth_headers):    
    if auth_headers:
        response = clear_message_queue(auth_headers)
        print(response.status_code)
        print(response.text)


