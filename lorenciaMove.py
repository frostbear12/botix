import pytesseract
import pyautogui
import time
import re  # Regular expressions
import win32api, win32con



def runBot(region_of_interest):

    def preprocess_image(image):
        # Convert to grayscale and apply other image processing techniques if necessary
        return image.convert('L')

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
        

    def click_and_hold(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)


    def release_click():
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def centerMouseAndWait(x=959, y=490, wait_duration=0.3):
        pyautogui.moveTo(x, y)
        time.sleep(wait_duration)


    def moveToLorRing(duration, interval, region, x_action_positions, y_action_positions, x_thresholds, y_thresholds, micro_movements):
        start_time = time.time()

        centerMouseAndWait()  # Center mouse and wait

        while time.time() - start_time < duration:
            coordinates = read_coordinates_from_screen(region)
            print("Extracted coordinates:", coordinates)

            if coordinates != "Coordinates not found":
                x_coord, y_coord = coordinates

                if x_coord in x_thresholds and y_coord in y_thresholds:
                    print("Target location achieved.")
                    release_click()  # Ensure all movements are stopped
                    return True

                # # Regular movement logic
                if x_coord < min(x_thresholds):
                    print("Moving Down!")
                    click_and_hold(*x_action_positions['down'])
                elif x_coord > max(x_thresholds):
                    print("Moving Up!")
                    click_and_hold(*x_action_positions['up'])

                if y_coord < min(y_thresholds):
                    print("Moving Right!")
                    click_and_hold(*y_action_positions['up'])
                elif y_coord > max(y_thresholds):
                    print("Moving Left!")
                    click_and_hold(*y_action_positions['down'])
                
                time.sleep(interval)

        release_click()  # Ensure movements are stopped if time runs out
        return False

    def click_at(x, y, wait=0.1):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)  # Mouse down
        time.sleep(wait)  # Wait for the specified duration
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)  # Mouse up

    def moveOverBridge(duration, interval, region, micro_movements, continue_action_position, acceptable_y_coords, x_thresholds, y_thresholds, x_action_positions, y_action_positions, x_bridge_thresholds, y_bridge_thresholds, y_bridge_action_position):
        centerMouseAndWait()  # Center mouse and wait

        initial_coordinates = read_coordinates_from_screen(region)
        if initial_coordinates != "Coordinates not found":
            x_coord, y_coord = initial_coordinates
            if x_coord in x_thresholds and y_coord in y_thresholds:
                print(f"Already at the target location: ({x_coord}, {y_coord}). Moving across the bridge.")
                moveAcrossTheBridge(interval, continue_action_position, x_bridge_thresholds, y_bridge_thresholds, y_bridge_action_position)
                return
            else:
                print("Not at target location. Re-executing moveToLorRing.")
                if not moveToLorRing(duration, interval, region, x_action_positions, y_action_positions, x_thresholds, y_thresholds, micro_movements):
                    print("Failed to reach the target location in the given time.")
                    return
                
        # Proceed with moveOverBridge logic
        start_time = time.time()
        is_clicking = False

        while time.time() - start_time < duration:
            coordinates = read_coordinates_from_screen(region)
            print("Extracted coordinates:", coordinates)

            if coordinates != "Coordinates not found":
                x_coord, y_coord = coordinates

                if y_coord in acceptable_y_coords:
                    print(f"Acceptable Y-coordinate {y_coord} reached. Transitioning to move across the bridge.")
                    moveAcrossTheBridge(interval, continue_action_position, x_bridge_thresholds, y_bridge_thresholds, y_bridge_action_position)
                    return

                if y_coord in micro_movements and not is_clicking:
                    click_and_hold(*micro_movements[y_coord])
                    time.sleep(interval)
                    release_click()
                    is_clicking = True

            time.sleep(interval)

        if not is_clicking:
            moveAcrossTheBridge(interval, continue_action_position, x_bridge_thresholds, y_bridge_thresholds, y_bridge_action_position)




    def moveAcrossTheBridge(interval, continue_action_position, x_target_thresholds, y_bridge_thresholds, y_bridge_action_position):
            centerMouseAndWait()  # Center mouse and wait
            is_clicking = False
            last_coordinates = None
            last_change_time = time.time()

            # Phase 1: Move until reaching the target X-coordinate
            while True:
                coordinates = read_coordinates_from_screen(region_of_interest)
                print("Extracted coordinates:", coordinates)

                if coordinates != "Coordinates not found":
                    x_coord, y_coord = coordinates

                    # Check if the current X-coordinate is within the target thresholds
                    if x_coord in x_target_thresholds:
                        print(f"Target X-coordinate {x_coord} reached. Moving to Y-coordinate adjustment.")
                        if is_clicking:
                            release_click()
                            is_clicking = False
                        break

                if not is_clicking:
                    print("Moving across the bridge...")
                    click_and_hold(*continue_action_position)
                    is_clicking = True

                time.sleep(interval)

            # Phase 2: Adjust Y-coordinate
            while True:
                coordinates = read_coordinates_from_screen(region_of_interest)
                print("Extracted coordinates:", coordinates)

                # Check if coordinates have changed
                if coordinates != "Coordinates not found":
                    if coordinates != last_coordinates:
                        last_coordinates = coordinates
                        last_change_time = time.time()

                    x_coord, y_coord = coordinates
                    if y_coord in y_bridge_thresholds:
                        print(f"Target Y-coordinate {y_coord} reached. Stopping movement.")
                        if is_clicking:
                            release_click()
                        break  # Exit the loop once target Y-coordinate is reached

                    # Check if coordinates have been the same for 5 seconds
                    if time.time() - last_change_time >= 5:
                        print("Coordinates unchanged for 5 seconds, performing right-click.")
                        if is_clicking:
                            release_click()
                            is_clicking = False
                        # Perform right-click
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                        time.sleep(1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                        time.sleep(0.3)

                        # CLICK HERE ONCE LEFT
                        click_at(1055, 598, wait=0.2)  # Perform a left-click at (1055, 598) with a 0.2 second wait
                        print("Performed a left-click at (1055, 598)")

                        last_change_time = time.time()  # Reset the timer

                if not is_clicking:
                    print("Adjusting Y-coordinate...")
                    click_and_hold(*y_bridge_action_position['left'])
                    is_clicking = True

                time.sleep(interval)

            # Call startHelper after reaching the target coordinates
            startHelper()


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

        time.sleep(0.7)


        # 6. Press "c" button on the keyboard
        win32api.keybd_event(0x43, 0, 0, 0)  # Press 'C'
        time.sleep(0.4)  # Short delay between down and up events for a more natural click
        win32api.keybd_event(0x43, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release 'C'

        # 7. End the script
        return False  # Indicate that runBot() should stop
    
        # Define the region of the screen you want to capture



    # Action positions for X and Y coordinates
    # UP = RIGHT, DOWN = LEFT
    y_action_positions = {'up': (1017, 463), 'down': (896, 524)}
    x_action_positions = {'up': (883, 428), 'down': (1011, 517)}




    # Thresholds for X and Y coordinates
    x_thresholds = {139, 140, 141}
    y_thresholds = {126, 127, 128}

    # Thresholds for X for move across the bridge
    x_bridge_thresholds = { 182, 183, 184, 185}  # Target X-coordinates
    y_bridge_thresholds = {116, 115, 114, 113, 112}  # Target Y-coordinates
    y_bridge_action_position = {'left': (888, 525)}  # Position to move left for Y-coordinate adjustment


    # Define the continue action position
    continue_action_position = (1077, 555)

    # Define micro movements for specific Y-coordinates
    micro_movements = {
        126: (997, 452),  # Micro movement coordinates for Y = 126
        128: (919, 511)   # Micro movement coordinates for Y = 128
    }



    acceptable_y_coords = {127}  # Include any other numbers as needed



    time.sleep(3)
    print("3 seconds to select the mu window")
    
    if moveToLorRing(60, 0.3, region_of_interest, x_action_positions, y_action_positions, x_thresholds, y_thresholds, micro_movements):
        print("Moving to the next phase: Over the bridge")
        moveOverBridge(60, 0.3, region_of_interest, micro_movements, continue_action_position, acceptable_y_coords, x_thresholds, y_thresholds, x_action_positions, y_action_positions, x_bridge_thresholds, y_bridge_thresholds, y_bridge_action_position)
    else:
        print("Failed to reach the target location in the given time.")



