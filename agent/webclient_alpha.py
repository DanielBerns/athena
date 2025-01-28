import contextlib
import json
import sys
from random import choices
from pathlib import Path 

import requests

root = 'http://127.0.0.1:5000'
create_bot_url = f'{root:s}/api/users'
tokens_url = f'{root:s}/api/tokens'
current_user_url = f'{root:s}/api/users/current'
all_the_messages_url = f'{root}/api/messages/all'

def create_bot(username, password):
    payload = {'username': username, 'password': password}
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

def empty_data(file_identifier):
    custom_data = {'username': '', 'password': '', 'register': ''}
    with open(file_identifier, 'w') as target:
         json.dump(custom_data, target)
    return custom_data

def load_data(file_identifier):
    try:
        with open(file_identifier, 'r') as source:
            some_data = json.load(source)
    except FileNotFoundError:
        print(f'{str(file_identifier):s} not found!')
        some_data = empty_data(file_identifier)
    except json.decoder.JSONDecodeError:
        print(f'{str(file_identifier):s} bad json!')
        some_data = empty_data(file_identifier)
    return some_data

def write_data(some_data, file_identifier):
    with open(file_identifier, 'w') as target:
         json.dump(some_data, target)

def report(response):
    status_code = response.status_code
    text = response.text
    print('status_code', status_code)
    print('*'*80)
    print(text)
    print('*'*80)                

def generate_randombot_data(secret_data_file_identifier):
    randombot_data = load_data(secret_data_file_identifier)
    source = 'abcdefghijklmnopqrstuvwxyz0123456789_()-+~'
    randombot_data['username'] = ''.join(choices(source, k=10))
    randombot_data['password'] = ''.join(choices(source, k=10))
    randombot_data['register'] = 'yes'
    write_data(randombot_data, secret_data_file_identifier)
    return randombot_data

def get_secret_fields(secret_data):
    try:
        username, password, register = secret_data['username'], secret_data['password'], secret_data['register']
    except KeyError as message:
        print('Error', str(message), '-', str(secret_data))
        username, password, register = '', '', ''
    return username, password, register


def get_all_the_messages(auth_headers):
    response = requests.get(all_the_messages_url, headers=auth_headers)
    return response


def get_messages(secret_data_file_identifier):    
    base_path = Path('~', 'Info', 'athena', 'webclient', 'store').expanduser()
    base_path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if secret_data_file_identifier == 'random':
        secret_data_file_identifier = Path(base_path, 'randombot.json')
        if secret_data_file_identifier.exists():
            secret_data = load_data(secret_data_file_identifier)
        else:
            secret_data = generate_randombot_data(secret_data_file_identifier)
    else:
        secret_data_file_identifier = Path(base_path, secret_data_file_identifier)
        secret_data = load_data(secret_data_file_identifier)
    username, password, register = get_secret_fields(secret_data)
    try:
        if len(username) == 0:
            raise ValueError("username unexpected null value")
        if len(password) == 0:
            raise ValueError("username unexpected null value")
        if  register == 'yes':
            print('Register')
            response = create_bot(username, password)
            report(response)
            secret_data['user'] = response.json()
            secret_data['register'] = "no"
            write_data(secret_data, secret_data_file_identifier)
        elif register == "no":
            print('No need to register user')
        else:
            raise ValueError(f"register unexpected value {register:s}")
    except ValueError as message:
        print('Error', str(message))
    else:
        print('Getting credentials')
        response = login_bot(username, password)
        report(response)
        if response.status_code == 200:
            print('Logged in')
            token_json = response.json()
            token = token_json['token']
            print('Get the token', token)
            auth_headers = get_token_headers(token)
            print('Get current user')
            response = get_current_user(auth_headers)
            report(response)
            print('Get current user received messages')
            response = get_all_the_messages(auth_headers)
            report(response)            
            as_json = response.json()
            items = as_json['items']
            print('#'*80)
            print('messages')
            for message in items:
                yield message


if __name__ == '__main__':
            
    if len(sys.argv) < 2:
        print('Error!!! Give me some data')
        sys.exit(1)
    secret_data_file_identifier = sys.argv[1]
    for message in get_messages(secret_data_file_identifier):
        print(message['id'], message['content'], message['sender_id'])
