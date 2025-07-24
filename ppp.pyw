import tkinter as tk
import os
import getpass
import platform
import socket

class FakeRansomwareCLI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransomware")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<space>", self.exit_program)

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
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.configure(state="disabled")

        # Gather real (local only) system info for scare factor
        username = getpass.getuser()
        computername = platform.node()
        ip_address = socket.gethostbyname(socket.gethostname())
        os_info = f"{platform.system()} {platform.release()}"

        user_dir_files = []
        try:
            user_dir = os.path.expanduser("~")
            sample_files = os.listdir(user_dir)
            user_dir_files = random.sample(sample_files, min(5, len(sample_files)))
        except:
            user_dir_files = ["[ERROR] Cannot access directory."]

        self.lines_to_type = [
            "[!] SYSTEM BREACH DETECTED...\n",
            "[*] Device Compromised\n",
            "[*] Collecting sensitive information...\n",
            "[*] Locking local data...\n",
            "\n",
            f"[INFO] Username: {username}\n",
            f"[INFO] Computer: {computername}\n",
            f"[INFO] Local IP: {ip_address}\n",
            f"[INFO] OS: {os_info}\n",
            "\n",
            "[!!!] YOUR FILES HAVE BEEN LOCKED\n",
            "[!!!] DO NOT POWER OFF OR DISCONNECT\n",
            "\n",
            "The following personal files are now inaccessible:\n"
        ]

        self.lines_to_type += [f"  - {f}" for f in user_dir_files]
        self.lines_to_type += [
            "\n",
            "We are monitoring your activity in real-time.\n",
            "Any attempt to bypass this lock will result in total data destruction.\n",
            "\n",
            "To recover your files, visit the TOR link below:\n",
            "http://decryptdata.onion/restore?id=AC7DFF91\n",
            "\n",
            "Your unique ID: AC7DFF91\n",
            "Time left: 47:59:33\n",
            "\n",
            "Press SPACEBAR to exit (your system will remain locked)\n"
        ]

        self.current_line = 0
        self.current_char = 0
        self.typing_speed_ms = 18
        self.start_typing()

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

    def exit_program(self, event):
        self.root.destroy()


if __name__ == "__main__":
    import random
    root = tk.Tk()
    app = FakeRansomwareCLI(root)
    root.mainloop()
