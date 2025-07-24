import tkinter as tk

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
            font=("Consolas", 16),  # Smaller font size
            bd=0,
            highlightthickness=0,
            padx=20,
            pady=20
        )
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.configure(state="disabled")

        self.lines_to_type = [
            "[!] SYSTEM COMPROMISED...\n",
            "[*] Establishing secure session with control node\n",
            "[*] Indexing critical files...\n",
            "[*] Locking data assets\n",
            "\n",
            "[!!!] ALL YOUR IMPORTANT FILES HAVE BEEN LOCKED\n",
            "[!!!] DO NOT TURN OFF YOUR COMPUTER\n",
            "\n",
            "Your documents, photos, databases, and other sensitive files are no longer accessible.\n",
            "You are being watched. Any attempt to tamper with the system will result in permanent loss.\n",
            "\n",
            "This is not a bluff.\n",
            "\n",
            "To recover your files, you must comply with the instructions provided below.\n",
            "Open the link on a TOR browser:\n",
            "http://darkgatedecrypt.onion/restore?id=AC7DFF91\n",
            "\n",
            "Your system ID: AC7DFF91\n",
            "Time remaining: 47:59:33\n",
            "\n",
            "Failure to act will result in irreversible data loss.\n",
            "\n",
            "Press SPACEBAR to exit (not recommended)\n"
        ]

        self.current_line = 0
        self.current_char = 0
        self.typing_speed_ms = 20  # milliseconds per character
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
                self.root.after(400, self.start_typing)
        else:
            pass

    def append_text(self, char):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", char)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def exit_program(self, event):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FakeRansomwareCLI(root)
    root.mainloop()
