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
from tkinter import Tk, Canvas, Toplevel



# scripts
from lorenciaMove import runBot
from dungeonMove import runDungeon
from moveSelectedWindow import move_window
from marryTrack import waitForMarryTrack
from checkForReset import checkIfRes
from addStats import run_stat_adder


script_thread = None
script_running = False

def start_script():
    global script_thread
    if script_thread is None or not script_thread.is_alive():
        script_thread = threading.Thread(target=run_scripts)
        script_thread.daemon = True  # Makes the thread terminate with the main program
        script_thread.start()
        update_log("Script started.")
    else:
        update_log("Script is already running.")


# Initialize pygame mixer
pygame.mixer.init()


# screen reading coords
locationCoords = (132, 36, 135, 25) # (left, top, width, height)
# levelCoords = (1400, 140, 150, 35) # (left, top, width, height)
levelCoords = (1400, 145, 130, 33) # (left, top, width, height)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # Base path for bundled application
        base_path = sys._MEIPASS
    except Exception:
        # Base path for normal execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def on_drag_start(event):
    overlay = event.widget.winfo_toplevel()
    overlay._drag_start_x = event.x_root
    overlay._drag_start_y = event.y_root


def update_coordinates_label():
    location_label.config(text=f"Location: {overlay1.winfo_x()}, {overlay1.winfo_y()}")
    level_label.config(text=f"Level: {overlay2.winfo_x()}, {overlay2.winfo_y()}")

def on_drag_motion(event):
    global locationCoords
    global levelCoords

    overlay = event.widget.winfo_toplevel()
    x = event.x_root - overlay._drag_start_x
    y = event.y_root - overlay._drag_start_y
    new_x = overlay.winfo_x() + x
    new_y = overlay.winfo_y() + y
    overlay.geometry(f"+{new_x}+{new_y}")
    overlay._drag_start_x = event.x_root
    overlay._drag_start_y = event.y_root
    update_coordinates_label()

    # Update the global coordinates based on which overlay is being moved
    if overlay == overlay1:
        locationCoords = (new_x, new_y, locationCoords[2], locationCoords[3])
    elif overlay == overlay2:
        levelCoords = (new_x, new_y, levelCoords[2], levelCoords[3])

def create_overlay(root, region, editable=True, color="green", border_width=5, handle_size=10):
    overlay = tk.Toplevel(root)
    overlay.attributes("-topmost", True)
    overlay.attributes("-transparentcolor", "white")
    overlay.overrideredirect(True)
    
    if editable :
        overlay.configure(cursor="fleur")

    # Create a Canvas for the overlay
    canvas = tk.Canvas(overlay, bg="white", width=region[2], height=region[3], highlightthickness=0)
    canvas.pack()

    # Draw border lines
    canvas.create_line(0, 0, region[2], 0, fill=color, width=border_width)
    canvas.create_line(0, 0, 0, region[3], fill=color, width=border_width)
    canvas.create_line(region[2], 0, region[2], region[3], fill=color, width=border_width)
    canvas.create_line(0, region[3], region[2], region[3], fill=color, width=border_width)

    # Create a draggable handle
    if editable :
        canvas.create_rectangle(0, 0, handle_size, handle_size, fill=color)


    # Position the overlay
    overlay.geometry(f"+{region[0]}+{region[1]}")

    if editable :
        # Bind mouse events for dragging
        canvas.bind("<Button-1>", on_drag_start)
        canvas.bind("<B1-Motion>", on_drag_motion)

    return overlay



def setup_tesseract():
    # Path to the root directory where the script is located
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

def update_log(message):
    log_text.config(state='normal')
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)
    log_text.config(state='disabled')

def start_move_window():
    def update_messages():
        def callback(message):
            root.after(0, lambda: update_log(message))

        move_window(callback)

    threading.Thread(target=update_messages, daemon=True).start()

# GUI Functions
def update_log(message):
    log_text.config(state='normal')
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)
    log_text.config(state='disabled')

def send_key_event(key_code, key_up=False):
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP if key_up else 0, 0)
    time.sleep(0.1)

def send_keys(string):
    for char in string:
        vk_code = win32api.VkKeyScan(char) & 0xFF
        send_key_event(vk_code)
        time.sleep(0.05)
        
def run_scripts():
    # Infinite loop to continuously run the script
    while True:
        current_phase = selected_phase.get()
        selectedClassFromBox = selected_class.get()
        userInputGrandResets = grand_resets_entry.get()

        try:
            grandResets = int(userInputGrandResets)
        except ValueError:
            grandResets = 0

        # Start from the selected phase and loop through all phases
        if current_phase in ["Start", "Stat Adder"]:
            update_log('Running Stat Adder Phase')
            run_stat_adder(selectedClassFromBox, grandResets, levelCoords)
            current_phase = "Run Lorencia"

        if current_phase in ["Run Lorencia"]:
            update_log('Running Lorencia Phase')
            runBot(locationCoords)
            current_phase = "Run Dungeon"

        if current_phase in ["Run Dungeon"]:
            update_log('Running Dungeon Phase')
            runDungeon(locationCoords, levelCoords)
            current_phase = "Marry Track"

        if current_phase in ["Marry Track"]:
            update_log('Running Marry Track Phase')
            waitForMarryTrack(levelCoords)
            current_phase = "Check Reset"

        if current_phase in ["Check Reset"]:
            update_log('Running Check Reset Phase')
            checkIfRes(levelCoords)
            current_phase = "Start"  # After finishing the last phase, start from the beginning

        # Small delay to prevent CPU overuse, adjust as needed
        time.sleep(0.1)

        # Check if GUI is still running; if not, break from the loop
        try:
            root.update_idletasks()
            root.update()
        except tk.TclError:
            break  # Break the loop if the root window is closed




def check_running():
    """Check if the script should continue running."""
    global script_running
    for _ in range(50):  # Check 50 times with 0.1 second delay each
        if not script_running:
            break
        time.sleep(0.1)


def release_all_mouse_clicks():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    update_log("All mouse clicks released.")






# GUI Setup
# Set the window icon
root = tk.Tk()
root.title("SUPER SEXUAL BOT")
root.geometry("600x400")
root.attributes("-topmost", True)

icon_path = resource_path('bot.ico')
root.iconbitmap(icon_path)

# Handling window close event
try:
    root.iconbitmap("bot.ico")  # Or the path to your icon file
except tk.TclError:
    pass



# Frame for class selection
class_selection_frame = tk.Frame(root)
class_selection_frame.pack(pady=5)  # Adjust padding as needed

# Class Selection Dropdown
class_label = tk.Label(class_selection_frame, text="Select class:")
class_label.pack(side=tk.LEFT, padx=5)  # Adjust side and padding as needed
class_options = ["BK", "SM", "ELF", "SUM", "DL", "RF", "MG"]
selected_class = tk.StringVar()
class_dropdown = tk.OptionMenu(class_selection_frame, selected_class, *class_options)
class_dropdown.pack(side=tk.LEFT)

# Frame for grand resets input
grand_resets_frame = tk.Frame(root)
grand_resets_frame.pack(pady=5)  # Adjust padding as needed

# Grand Resets Input
grand_resets_label = tk.Label(grand_resets_frame, text="Grand Resets:")
grand_resets_label.pack(side=tk.LEFT, padx=5)  # Adjust side and padding as needed
grand_resets_entry = tk.Entry(grand_resets_frame)
grand_resets_entry.pack(side=tk.LEFT)

# Define your phases
phases = ["Start", "Stat Adder", "Run Lorencia", "Run Dungeon", "Marry Track", "Check Reset"]

# Frame for the phase selection dropdown
phase_selection_frame = tk.Frame(root)
phase_selection_frame.pack(pady=5)  # Adjust padding as needed
# Label for the phase selection dropdown
phase_label = tk.Label(phase_selection_frame, text="Select Phase:")
phase_label.pack(side=tk.LEFT, padx=5)  # Adjust side and padding as needed

# Dropdown for phase selection
selected_phase = tk.StringVar()
selected_phase.set(phases[0])  # default value
phase_dropdown = tk.OptionMenu(phase_selection_frame, selected_phase, *phases)
phase_dropdown.pack(side=tk.LEFT)


# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)  # Add some vertical padding

# Add Start Script Button to the GUI
start_script_button = tk.Button(button_frame, text="Start Script", command=start_script)
start_script_button.pack(side=tk.LEFT, padx=5)

# Center Window Button
center_window_button = tk.Button(button_frame, text="Center Window", command=start_move_window)
center_window_button.pack(side=tk.LEFT, padx=5)

def on_closing():
    os._exit(0)

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

# Dont place rectangles
rec1coords = (0, 850, 880, 150)
rectangleOverlay1 = create_overlay(root, rec1coords, False, "red")
rec2coords = (1388, 900, 500, 80)
rectangleOverlay1 = create_overlay(root, rec2coords, False, "red")
rec3coords = (750, 200, 500, 600)
rectangleOverlay1 = create_overlay(root, rec3coords, False, "red")


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
