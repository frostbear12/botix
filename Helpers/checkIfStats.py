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
stat_image_path = resource_path('Helpers/Images/stat_panel.png')

def is_stat_screen_open(num_attempts=1, delay=2):
    """
    Checks if the character stat screen is open by searching for a reference image on the screen.
    Attempts the check multiple times with a short delay between each attempt.

    Args:
        reference_image_path (str): The file path to the reference image.
        num_attempts (int): Number of attempts to check for the image.
        delay (float): Delay in seconds between each attempt.

    Returns:
        bool: True if the reference image is found on the screen within the given attempts, False otherwise.
    """
    for _ in range(num_attempts):
        try:
            location = pyautogui.locateOnScreen(stat_image_path, confidence=0.8)
            if location is not None:
                return True
        except:
            pass
        time.sleep(delay)
    return False


def open_stat_screen(executionPlace="", retries=2, delay=4):
    """
    Attempts to open the stat screen up to a specified number of retries.
    
    Args:
        retries (int): Number of times to attempt opening the stat screen.
        delay (int): Delay in seconds between attempts.
    
    Returns:
        bool: True if the stat screen is successfully opened, False otherwise.
    """
    for attempt in range(retries):
        if is_stat_screen_open(num_attempts=1, delay=delay):
            print(f"Stat screen is open (Attempt {attempt + 1}).")
            return True
        else:
            print(f"From {executionPlace}: Stat screen is not open. Attempting to open it (Attempt {attempt + 1})...")
            # Press 'C' to open the stats screen
            win32api.keybd_event(67, 0, 0, 0)  # Key down 'C'
            time.sleep(0.1)
            win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up 'C'
            time.sleep(delay)  # Wait for the screen to potentially open

    print("Failed to open stat screen after multiple attempts.")
    return False

