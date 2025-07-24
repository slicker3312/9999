import tkinter as tk

def on_space(event):
    root.destroy()

def toggle_colors():
    global flash_state
    flash_state = not flash_state

    bg_color = "white" if flash_state else "black"
    fg_color = "black" if flash_state else "red"

    root.configure(bg=bg_color)
    label.configure(bg=bg_color, fg=fg_color)

    root.after(300, toggle_colors)  # speed of flashing (ms)

# Setup window
root = tk.Tk()
root.title("You've Been Hacked")
root.attributes("-fullscreen", True)
root.bind("<space>", on_space)

# Text label
label = tk.Label(
    root,
    text="YOU HAVE BEEN HACKED",
    font=("Courier", 60, "bold")
)
label.pack(expand=True)

# Start flashing
flash_state = False
toggle_colors()

# Start GUI
root.mainloop()
