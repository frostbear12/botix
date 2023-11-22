import pytesseract
import pyautogui
import time
import re  # Regular expressions
import win32api, win32con
import win32com.client  # For sending keystrokes



def waitForMarryTrack(levelRegion):
    time.sleep(3)


    def preprocess_image(image):
        # Convert to grayscale
        gray_image = image.convert('L')
        # Increase contrast here if necessary, e.g., using ImageEnhance from PIL
        return gray_image

    # # Extract levels
    def read_levels_from_screen(region):
        # Take a screenshot of the specified region
        screenshot = pyautogui.screenshot(region=region)

        # Preprocess the image for better OCR results
        processed_image = preprocess_image(screenshot)

        # Use Tesseract to do OCR on the image without any additional configurations
        full_text = pytesseract.image_to_string(processed_image)
        
        # Use a regular expression to search for the pattern "Level: [number] |"
        match = re.search(r'Level:\s*(\d+)\s*\|', full_text)
        if match:
            # Extract the level number and return it
            level_number = match.group(1)
            return level_number  # This will be a string containing only the level number
        else:
            # If the pattern is not found, return an indicator such as "Level not found"
            return "Level not found"
        # Then, later in your code, you can call this function and print the result:
    def readLevels():
        level = read_levels_from_screen(levelRegion)
        if level and level.isdigit():  # Check if the result is a number and not None
            print("Current Level:", level)
            return level
        else:
            print("Level not found or not a number")
            return "0"  # Return "0" as a string if level is not found
   
    def key_down(key):
        win32api.keybd_event(key, 0, 0, 0)

    def key_up(key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    def send_keys(str):
        for char in str:
            if char.isupper() or char == '/':
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Hold Shift
            vk_code = win32api.VkKeyScan(char)
            key_down(vk_code)
            key_up(vk_code)
            if char.isupper() or char == '/':
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Shift

    def centerMouseAndWait(x=959, y=490, wait_duration=1.0):
        # Set cursor position to the specified coordinates
        win32api.SetCursorPos((x, y))
        # Wait for the specified duration
        time.sleep(wait_duration)

    def startHelper():
        # 1. Center the mouse and wait
        centerMouseAndWait()

        # 2. Move the mouse to location (1088, 328)
        win32api.SetCursorPos((441, 40))

        # 3. Wait 0.7 seconds
        time.sleep(0.7)

        # 4. Click on that target
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.4)  # Short delay between down and up events for a more natural click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        time.sleep(0.7)

        # 5. Cast "centerMouseAndWait" again
        centerMouseAndWait()

        # 6. Press "c" button on the keyboard
        win32api.keybd_event(0x43, 0, 0, 0)  # Press 'C'
        time.sleep(0.4)  # Short delay between down and up events for a more natural click
        win32api.keybd_event(0x43, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release 'C'

        # 7. End the script
        return False  # Indicate that runBot() should stop

    # warp action
    def send_key_event(key_code):
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)  # Slight delay to simulate real key press
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

    def send_warp_command():
        send_key_event(win32con.VK_RETURN)  # Press Enter
        time.sleep(0.5)
        
        # Type "marry track"
        for char in "/marry track":
            vk_code = win32api.VkKeyScan(char)
            send_key_event(vk_code & 0xFF)  # VkKeyScan returns a tuple
        time.sleep(0.5)
        
        send_key_event(win32con.VK_RETURN)  # Press Enter again

        # wait for 1 second
        time.sleep(1)

        send_key_event(win32con.VK_RETURN)  # Press Enter again

        # wait for 4 second
        time.sleep(4)

        # Now call moveToSpotAndNavigate right after sending the command
        startHelper()

    # The loop now indefinitely checks for the level
    while True:
        current_level = readLevels()
        if current_level.isdigit() and int(current_level) >= 150:
            print(f"Reached level {current_level}, executing warp command.")
            send_warp_command()
            break  # Break the loop after sending the warp command
        else:
            print(f"Current level {current_level}, waiting for level 322.")
        time.sleep(5)  # Delay to prevent spamming
        