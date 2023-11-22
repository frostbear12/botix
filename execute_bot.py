import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import os
import sys
import win32api
import win32con
import keyboard
import signal
import pygame  # Import pygame
import pytesseract
from PIL import Image, ImageTk, ImageDraw



# scripts
from lorenciaMove import runBot
from dungeonMove import runDungeon
from moveSelectedWindow import move_window
from marryTrack import waitForMarryTrack
from checkForReset import checkIfRes
from addStats import run_stat_adder

# Global variables
script_running = False
paused = False
script_thread = None

# Initialize pygame mixer
pygame.mixer.init()

# screen reading coords
locationCoords = (132, 36, 135, 25) # (left, top, width, height)
# levelCoords = (1400, 140, 150, 35) # (left, top, width, height)
levelCoords = (1400, 145, 110, 33) # (left, top, width, height)

def on_drag_start(event):
    overlay = event.widget.winfo_toplevel()
    overlay._drag_start_x = event.x_root
    overlay._drag_start_y = event.y_root


def update_coordinates_label():
    location_label.config(text=f"Location: {overlay1.winfo_x()}, {overlay1.winfo_y()}")
    level_label.config(text=f"Level: {overlay2.winfo_x()}, {overlay2.winfo_y()}")

def on_drag_motion(event):
    overlay = event.widget.winfo_toplevel()
    x = event.x_root - overlay._drag_start_x
    y = event.y_root - overlay._drag_start_y
    new_x = overlay.winfo_x() + x
    new_y = overlay.winfo_y() + y
    overlay.geometry(f"+{new_x}+{new_y}")
    overlay._drag_start_x = event.x_root
    overlay._drag_start_y = event.y_root
    update_coordinates_label()

def create_overlay(root, region, color="green", border_width=5):
    overlay = tk.Toplevel(root)
    overlay.attributes("-topmost", True)
    overlay.attributes("-transparentcolor", "white")
    overlay.overrideredirect(True)
    overlay.configure(cursor="fleur")  # Correct way to set cursor style

    # Create a Canvas for the overlay
    canvas = tk.Canvas(overlay, bg="white", width=region[2], height=region[3], highlightthickness=0)
    canvas.pack()

    # Draw border lines
    canvas.create_line(0, 0, region[2], 0, fill=color, width=border_width)  # Top
    canvas.create_line(0, 0, 0, region[3], fill=color, width=border_width)  # Left
    canvas.create_line(region[2], 0, region[2], region[3], fill=color, width=border_width)  # Right
    canvas.create_line(0, region[3], region[2], region[3], fill=color, width=border_width)  # Bottom

    # Position the overlay
    overlay.geometry(f"+{region[0]}+{region[1]}")

    # Bind mouse events for dragging
    canvas.bind("<Button-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag_motion)

    return overlay




def setup_tesseract():
    # Check if the script is running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        basedir = sys._MEIPASS  # This is the temporary directory for PyInstaller
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the Tesseract executable
    tesseract_cmd = os.path.join(basedir, 'Tesseract-OCR', 'tesseract.exe')

    # Set the Tesseract command
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Call the setup function at the beginning of your script
setup_tesseract()


def play_start_sound():
    try:
        pygame.mixer.music.load('audio/bot_started.mp3')  # Load your MP3 file from the 'audio' subfolder
        pygame.mixer.music.play()
    except Exception as e:
        update_log(f"Failed to play sound: {e}")


# Custom class to redirect standard output to the log text widget
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.config(state='normal')
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)
        self.widget.config(state='disabled')

    def flush(self):
        pass

# GUI Functions
def update_log(message):
    log_text.config(state='normal')
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)
    log_text.config(state='disabled')

def safe_exit_sequence():
    print("Executing safe exit sequence and restarting...")
    send_key_event(win32con.VK_RETURN)  # Press Enter
    time.sleep(0.1)
    send_key_event(win32con.VK_RETURN, key_up=True)  # Release Enter
    send_keys("/warp lorencia")
    send_key_event(win32con.VK_RETURN)  # Press Enter
    time.sleep(0.1)
    send_key_event(win32con.VK_RETURN, key_up=True)  # Release Enter
    time.sleep(3)  # Wait for the warp action to complete


def send_key_event(key_code, key_up=False):
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP if key_up else 0, 0)
    time.sleep(0.1)

def send_keys(string):
    for char in string:
        vk_code = win32api.VkKeyScan(char) & 0xFF
        send_key_event(vk_code)
        time.sleep(0.05)

def pause_resume_script():
    global paused
    paused = not paused
    update_log(f"Script {'paused' if paused else 'resumed'}.")

def pause_resume_script():
    global paused
    paused = not paused
    print(f"Script {'paused' if paused else 'resumed'}.")

def run_scripts():
    global paused, script_running
    update_log("Script started running.")
    while script_running:
        if paused:
            time.sleep(1)
            continue

        try:
            selectedClassFromBox = selected_class.get()  # Get the selected class from the dropdown
            userInputGrandResets = grand_resets_entry.get()  # Get user input for grand resets

            # Try to convert the grand resets input to an integer
            try:
                grandResets = int(userInputGrandResets)
            except ValueError:
                # If conversion fails, log an error and use a default value (e.g., 0)
                update_log("Invalid grand resets input. Using default value 0.")
                grandResets = 0

            update_log("Running scripts...")
            # Your script functionality

            # Small pause
            time.sleep(1)


            # Runs the stat adder
            run_stat_adder(selectedClassFromBox, grandResets, levelCoords)

            # Runs the bot itself for lorencia sequence
            runBot(locationCoords)

            # Runs the bot for dungeon sequence
            runDungeon(locationCoords, levelCoords)

            # Waits until it can get to spot with marry track
            waitForMarryTrack(levelCoords)

            # Checks if there is a reset
            checkIfRes(levelCoords)

        except Exception as e:
            update_log(f"An error occurred: {e}. Executing safe exit...")
            safe_exit_sequence()
            time.sleep(5)  # Wait some time before restarting
            continue  # Restart the loop after the safe exit sequence

        time.sleep(1)

    update_log("Script stopped running.")

def start_stop_script():
    global script_running, script_thread
    if not script_running:
        script_running = True
        script_thread = threading.Thread(target=run_scripts)
        script_thread.start()
        start_stop_button.config(text="Stop Script")
        update_log("Script started.")
        play_start_sound()  # Play sound when the script starts
    else:
        script_running = False
        if script_thread.is_alive():
            # Give some time for the script to stop gracefully
            script_thread.join(timeout=5)
            if script_thread.is_alive():
                # If the script is still running, force stop
                update_log("Failed to stop script gracefully, forcing stop...")
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                update_log("Script stopped successfully.")
                release_all_mouse_clicks()  # Release mouse clicks when the script stops
        start_stop_button.config(text="Start Script")

def release_all_mouse_clicks():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    update_log("All mouse clicks released.")

def on_hotkey_pressed():
    global script_running
    update_log("Hotkey pressed, attempting to stop script gracefully...")
    script_running = False
    if script_thread.is_alive():
        script_thread.join(timeout=3)  # Wait for max 3 seconds for the script thread to finish

    if script_thread.is_alive():
        # If the script is still running after 3 seconds, force stop
        update_log("Failed to stop script gracefully, forcing stop...")
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        update_log("Script stopped successfully.")
        release_all_mouse_clicks()  # Release mouse clicks when the script is stopped by the hotkey

keyboard.add_hotkey('*', on_hotkey_pressed)


keyboard.add_hotkey('*', on_hotkey_pressed)


# GUI Setup
root = tk.Tk()
root.title("SUPER SEXUAL BOT")
root.geometry("400x400")
root.attributes("-topmost", True)  # Keep the main window always on top

# Center Window Button
center_window_button = tk.Button(root, text="Center Window", command=move_window)
center_window_button.pack()


# Class Selection Dropdown
class_label = tk.Label(root, text="Select class:")
class_label.pack()
class_options = ["BK", "SM", "ELF", "SUM", "DL", "RF", "MG"]
selected_class = tk.StringVar()
class_dropdown = tk.OptionMenu(root, selected_class, *class_options)
class_dropdown.pack()

# Grand Resets Input
grand_resets_label = tk.Label(root, text="Grand Resets:")
grand_resets_label.pack()
grand_resets_entry = tk.Entry(root)
grand_resets_entry.pack()

# Start/Stop Button
start_stop_button = tk.Button(root, text="Start Script", command=start_stop_script)
start_stop_button.pack()

# Pause Button
# pause_button = tk.Button(root, text="Pause/Resume Script", command=pause_resume_script)
# pause_button.pack()


# Log Text Area
log_text = scrolledtext.ScrolledText(root, state='disabled', height=10)
log_text.pack()

# Redirect standard output to the log text widget
sys.stdout = TextRedirector(log_text)

location_label = tk.Label(root, text="Location: 132, 36")
location_label.pack()

level_label = tk.Label(root, text="Level: 1400, 145")
level_label.pack()

# Create overlays as part of the main application
overlay1 = create_overlay(root, locationCoords)
overlay2 = create_overlay(root, levelCoords)

root.mainloop()