import pyautogui
import time
import win32api
import win32con
import os
import sys

def resource_path(relative_path):
    """ Get the correct path for resources both for development and after compiling. """
    try:
        base_path = sys._MEIPASS  # Compiled path
    except Exception:
        base_path = os.path.abspath(".")  # Current directory

    return os.path.join(base_path, relative_path)

# Correct path to the image
enter_image_path = resource_path('Helpers/Images/enterPressed.png')

def is_enter_window_open(confidence_level=0.8):
    try:

        location = pyautogui.locateOnScreen(enter_image_path, confidence=confidence_level)
        return location is not None
    except:
        return False

def open_enter_window_if_closed(retries=2, delay_between_attempts=3):
    """
    Checks if the 'Enter' input window is open, and if not, attempts to open it by simulating an 'Enter' key press.

    Args:
        retries (int): Number of attempts to check and open the window.
        delay_between_attempts (int): Delay in seconds between each attempt.

    Returns:
        bool: True if the 'Enter' window is successfully opened, False otherwise.
    """
    for attempt in range(retries):
        if is_enter_window_open():
            print(f"Enter window is open (Attempt {attempt + 1}).")
            return True
        else:
            print(f"Enter window is not open. Attempting to open it (Attempt {attempt + 1})...")
            # Simulate pressing 'Enter' key
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)  # Key down 'Enter'
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up 'Enter'
            time.sleep(delay_between_attempts)  # Wait for the screen to potentially open

    print("Failed to open Enter window after multiple attempts.")
    return False
