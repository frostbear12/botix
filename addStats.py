import win32api
import win32con
import pytesseract
import pyautogui
import re
import time

def run_stat_adder(selectedClassFromBox, grandResets, resetRegion):
    def move_and_click(x, y):
        time.sleep(0.5)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def send_key_event(key_code, shift=False):
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Hold Shift
        win32api.keybd_event(key_code, 0, 0, 0)  # Key down
        time.sleep(0.05)  # Short delay
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Shift

    def send_keys(string):
        for char in string:
            shift = char.isupper() or char in [' ']
            if char == '/':
                vk_code = 0xBF  # Manually set VK code for '/'
            else:
                vk_code = win32api.VkKeyScan(char) & 0xFF
            send_key_event(vk_code, shift)
            time.sleep(0.05)  # Delay between each key press

    def add_stats(stat_type, points):
        command = f"/{stat_type} {points}"
        send_key_event(win32con.VK_RETURN)  # Press Enter
        time.sleep(0.5)
        send_keys(command)
        send_key_event(win32con.VK_RETURN)  # Press Enter
        time.sleep(1)

    def read_resets_from_screen(region):
        screenshot = pyautogui.screenshot(region=region)
        gray_image = screenshot.convert('L')
        full_text = pytesseract.image_to_string(gray_image)
        match = re.search(r'R:\s*(\d+)', full_text)
        if match:
            resets = int(match.group(1))
            return resets
        else:
            return "Resets not found"

    def read_resets_with_retries(region, max_attempts=3):
        attempts = 0
        while attempts < max_attempts:
            resets = read_resets_from_screen(region)
            if isinstance(resets, int):
                return resets  # Successfully read resets
            print(f"Attempt {attempts + 1}/{max_attempts} failed to read resets. Retrying...")
            attempts += 1
            time.sleep(1)  # Wait a bit before retrying
        return "Resets not found"  # Return this if all attempts fail

    def calculate_available_stats(resets, selectedClass, grandResets):
        multiplier = 800 if selectedClass in ["BK", "SM", "ELF", "SUM"] else 900
        return resets * multiplier + (grandResets * 5000)

    def distribute_stats(availableStats, selectedClass):
        # Blade Knight (BK)
        if selectedClass == "BK":
            energy = 450
            vitality = 1000
            remaining = availableStats - (energy + vitality)
            agility = int(0.4 * remaining)
            strength = int(0.6 * remaining)
            return {"ene": energy, "vit": vitality, "agi": agility, "str": strength}

        # Soul Master (SM)
        elif selectedClass == "SM":
            strength = 500
            vitality = 1000
            remaining = availableStats - (strength + vitality)
            agility = int(0.4 * remaining)
            energy = int(0.6 * remaining)
            return {"str": strength, "vit": vitality, "agi": agility, "ene": energy}

        # Magic Gladiator (MG)
        elif selectedClass == "MG":
            strength = 800
            vitality = 1000
            remaining = availableStats - (strength + vitality)
            agility = int(0.4 * remaining)
            energy = int(0.6 * remaining)
            return {"str": strength, "vit": vitality, "agi": agility, "ene": energy}

        # If the class is not one of the above, distribute stats evenly
        else:
            stat_value = int(availableStats / 4)  # Divide the available stats evenly
            return {"str": stat_value, "vit": stat_value, "agi": stat_value, "ene": stat_value}
   
    # Move mouse and click at specified position before starting the reset checks
    move_and_click(1600, 1055)

    # Wait 2 seconds
    time.sleep(2)

    # Use the read_resets_with_retries function
    resets = read_resets_with_retries(resetRegion)
    if isinstance(resets, int):
        availableStats = calculate_available_stats(resets, selectedClassFromBox, grandResets)
        statDistribution = distribute_stats(availableStats, selectedClassFromBox)
        print(f"Resets: {resets}, Available Stats: {availableStats}, Distribution: {statDistribution}")

        # Add stats in the game
        for stat_type, points in statDistribution.items():
            add_stats(stat_type, points)
        print("Finished adding stats.")

    else:
        print("Resets:", resets)

    # Move mouse and click again after adding stats
    move_and_click(1600, 1055)

    print("Script completed. Pausing for 3 seconds...")
    time.sleep(3)
