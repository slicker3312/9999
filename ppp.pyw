import tkinter as tk
import time

class FakeRansomwareCLI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransomware Alert")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<space>", self.exit_program)

        self.text_widget = tk.Text(
            root,
            bg="black",
            fg="lime",
            insertbackground="lime",
            font=("Consolas", 20),
            bd=0,
            highlightthickness=0,
            padx=20,
            pady=20
        )
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.configure(state="disabled")

        self.lines_to_type = [
            "Initializing encryption process...\n",
            "Scanning files in user directories...\n",
            "Encrypting files with AES-256...\n",
            "Backing up encryption keys to remote server...\n",
            "\n",
            "YOUR FILES HAVE BEEN ENCRYPTED!\n",
            "To recover your files, you must pay 5 BTC to the following address:\n",
            "1FfmbHfnpaZjKFvyi1okTjJJusN455paPH\n",
            "\n",
            "Send the payment within 48 hours, or your files will be permanently deleted.\n",
            "After payment, contact us at decrypt_support@onionmail.org with your wallet address.\n",
            "\n",
            "Press SPACEBAR to exit (Not recommended, your files will remain encrypted)\n"
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
                # Slight delay between lines for realism
                self.root.after(400, self.start_typing)
        else:
            # Finished typing all lines
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
