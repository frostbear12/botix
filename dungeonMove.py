import pytesseract
import pyautogui
import time
import re  # Regular expressions
import win32api, win32con
from Helpers.checkIfStats import open_stat_screen  # Import the function
from Helpers.checkIfEnter import open_enter_window_if_closed, is_enter_window_open




def runDungeon(coordinateRegion, levelRegion):
    global helperStarted  # Declare the variable at the start of the function
    helperStarted = False  # Initialize it to False
    
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

        # 2. Move the mouse to location (441, 40)
        win32api.SetCursorPos((441, 45))

        # 3. Wait 0.7 seconds
        time.sleep(0.7)

        # 4. Click on that target
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 441, 40, 0, 0)
        time.sleep(0.4)  # Short delay between down and up events for a more natural click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 441, 40, 0, 0)

        # 5. Wait 0.7 seconds
        time.sleep(0.7)

        # 6. Alternative way to press 'C' using mouse movement and click
        win32api.SetCursorPos((1600, 1055))  # Move mouse to specific coordinates
        time.sleep(0.5)  # Wait

        # Perform click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 1600, 1055, 0, 0)
        time.sleep(0.1)  # Delay between mouse down and up for a click effect
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 1600, 1055, 0, 0)

        # 7. Wait 0.5 seconds and re-center the mouse
        time.sleep(0.5)
        centerMouseAndWait()

        # End the script
        return False  # Indicate that the function should stop



    def preprocess_image(image):
        # Convert to grayscale
        gray_image = image.convert('L')
        # Increase contrast here if necessary, e.g., using ImageEnhance from PIL
        return gray_image

    def read_coordinates_from_screen(region):
        # Take a screenshot of the specified region
        screenshot = pyautogui.screenshot(region=region)

        # Preprocess the image for better OCR results
        processed_image = preprocess_image(screenshot)

        # Use Tesseract to do OCR on the image
        full_text = pytesseract.image_to_string(processed_image, config='--psm 6')

        # Extract coordinates using regular expression
        match = re.search(r'(\d{3})\s*,\s*(\d{3})', full_text)
        if match:
            coordinates = match.groups()
            return tuple(map(int, coordinates))  # Convert the coordinates to integers
        else:
            return "Coordinates not found"
        
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
            print("Current Level (dungeon level read):", level)
            return level
        else:
            print("Level not found or not a number (dungeons level read)")
            return "0"  # Return "0" as a string if level is not found
        


    # warp action
    def send_key_event(key_code):
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)  # Slight delay to simulate real key press
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

    def send_warp_command():
        print("Sleep : 1 second")
        time.sleep(0.5)

        send_key_event(win32con.VK_RETURN)  # Press Enter
        time.sleep(0.5)

        # Ensure the Enter window is open before typing
        if not is_enter_window_open():
            open_enter_window_if_closed()
        
        # Type "/warp dungeon2"
        for char in "/warp dungeon2":
            if char == '/':
                # For special characters like '/', Shift needs to be held down
                send_key_event(win32con.VK_SHIFT)
            vk_code = win32api.VkKeyScan(char)
            send_key_event(vk_code & 0xFF)  # VkKeyScan returns a tuple
            
            if char == '/':
                # Release Shift after typing '/'
                send_key_event(win32con.VK_SHIFT)
        time.sleep(0.5)
        
        send_key_event(win32con.VK_RETURN)  # Press Enter again
        time.sleep(0.5)

        # Verify that the Enter window is closed
        if is_enter_window_open():
            print("Enter window did not close as expected.")
        else:
            print("Enter window closed successfully.")



    def moveToSpotAndNavigate():
        global helperStarted
        centerMouseAndWait()
        x_coord, y_coord = None, None

        # Check for X coordinate and warp if necessary
        while True:
            coordinates = read_coordinates_from_screen(coordinateRegion)
            print("Extracted coordinates:", coordinates)
            if coordinates != "Coordinates not found":
                x_coord, y_coord = coordinates

                if x_coord == 233:
                    send_warp_command()
                    time.sleep(2)
                    centerMouseAndWait()
                elif x_coord in [232, 231]:
                    print("Correct position reached, preparing to move.")
                    break
                else:
                    print("Waiting to reach correct X coordinate...")
            else:
                print("Failed to read coordinates")
            time.sleep(0.5)

        # Center mouse cursor
        centerMouseAndWait()

        # Click and hold to move
        click_and_hold(756, 590)

        # Move character until reaching target Y coordinate
        while not y_coord in [110, 109, 108, 107]:
            coordinates = read_coordinates_from_screen(coordinateRegion)
            print("Extracted coordinates during movement:", coordinates)
            if coordinates != "Coordinates not found":
                _, y_coord = coordinates
            else:
                print("Waiting to reach target Y coordinate...")
            time.sleep(0.15)

        # Release click
        release_click()

        # Start helper if not already started
        if not helperStarted:
            print("Target coordinates reached, executing startHelper.")
            startHelper()
            helperStarted = True

        print("Movement completed.")

    def click_and_hold(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)

    def release_click():
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # Wait for 2 seconds before the script starts
    print("Sleep : 2 second")
    time.sleep(2)



    # Main loop of the function
    while True:
        current_level = readLevels()
        
        if current_level == "0":
            print("Failed to read level. Attempting to open stat screen...")
            if not open_stat_screen():
                print("Failed to open stat screen. Retrying level read after delay.")
                time.sleep(5)  # Delay before retrying
                continue  # Skip the rest of this loop iteration

        if current_level.isdigit() and int(current_level) >= 40:
            print(f"Reached level {current_level}, executing warp command.")
            send_warp_command()
            time.sleep(2)
            moveToSpotAndNavigate()
            break
        else:
            print(f"Current level {current_level}, waiting for level 40.")
        time.sleep(5)  # Delay to prevent spamming

    print("Dungeon run completed.")


