import keyboard
import sys

#defining what a keystroke is 

def keystroke(e):
    print(f'Key {e.name} was {e.event_type}')

log = keyboard.hook(keystroke)
original_stdout = sys.stdout

# Keep the program running

keyboard.wait('esc')  

# Waits until user presses esc (for debugging purposes)
print(log)

