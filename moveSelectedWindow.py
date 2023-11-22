import win32gui
import win32con
import time

def move_window():
    def get_foreground_window():
        return win32gui.GetForegroundWindow()

    def get_window_title(hwnd):
        return win32gui.GetWindowText(hwnd)

    # Wait for 5 seconds to allow the user to select the window
    print("Please select the window to move. You have 5 seconds.")
    time.sleep(5)

    # Get the handle and title of the currently active window
    foreground_window = get_foreground_window()
    window_title = get_window_title(foreground_window)

    # Check if the selected window is the correct one
    if "EliteMU.net - S6 E3 Original" in window_title:
        # Move the window to the top-left corner
        rect = win32gui.GetWindowRect(foreground_window)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        win32gui.MoveWindow(foreground_window, 0, 0, width, height, True)
        print("Window moved successfully.")
    else:
        print("No MU window selected. Exiting script.")

# Now in your main script, you can call move_window without arguments
# move_window()
