import pytesseract
import pyautogui
import time
import re  # Regular expressions
import win32api, win32con
from Helpers.checkIfStats import open_stat_screen

def checkIfRes(levelRegion):
        while True:
                try:
                    time.sleep(60)  # Wait for one minute before checking the level again

                    current_level = readLevels(levelRegion)
                    if current_level == "0":
                        print("Failed to read level. Attempting to open stat screen...")
                        if not open_stat_screen("RESET CHECKER"):
                            print("Failed to open stat screen. Retrying level read after delay.")
                            continue  # Skip the rest of this loop iteration

                    if current_level.isdigit() and int(current_level) >= 400:
                        print(f"Reached level {current_level}, executing warp command.")
                        send_reset_command()
                        break
                    else:
                        print(f"Current level {current_level}, waiting for level 400.")
                except Exception as e:
                    print(f"An error occurred: {e}. Restarting the check...")
                    continue  # Continue the while loop, hence restarting the check

def readLevels(levelRegion):

    # Preprocess the image for better OCR results
    screenshot = pyautogui.screenshot(region=levelRegion)
    processed_image = preprocess_image(screenshot)

    # Use Tesseract to do OCR on the image
    full_text = pytesseract.image_to_string(processed_image)

    match = re.search(r'Level:\s*(\d+)\s*\|', full_text)
    if match:
        level_number = match.group(1)
        return level_number
    else:
        return "0"  # Return "0" as a string if level is not found

def preprocess_image(image):
    # Convert to grayscale
    gray_image = image.convert('L')
    return gray_image

def send_reset_command():
    # Step 1: Wait 0.5 seconds
    time.sleep(0.5)

    # Step 2: Press "C" with mouse down 0.1 delay and mouse up
    win32api.keybd_event(67, 0, 0, 0)  # Key down 'C'
    time.sleep(0.1)
    win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up 'C'

    # Step 3: Click mouse on (1800, 971)
    win32api.SetCursorPos((1800, 971))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 1800, 971, 0, 0)
    time.sleep(0.05)  # Slight delay to simulate a real click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 1800, 971, 0, 0)

    # Step 4: Wait 0.5 seconds
    time.sleep(0.5)

    # Step 5: Move mouse to (800, 415) and click
    win32api.SetCursorPos((800, 415))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 800, 415, 0, 0)
    time.sleep(0.1)  # Slight delay to simulate a real click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 800, 415, 0, 0)

    return

