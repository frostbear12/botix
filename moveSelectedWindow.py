import win32gui
import win32con
import time

def move_window(update_callback):
    def get_foreground_window():
        return win32gui.GetForegroundWindow()

    def get_window_title(hwnd):
        return win32gui.GetWindowText(hwnd)

    for i in range(5, 0, -1):
        update_callback(f"Please select the window to move. You have {i} seconds.")
        time.sleep(1)

    foreground_window = get_foreground_window()
    window_title = get_window_title(foreground_window)

    if "EliteMU.net - S6 E3 Original" in window_title:
        rect = win32gui.GetWindowRect(foreground_window)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        win32gui.MoveWindow(foreground_window, 0, 0, width, height, True)
        update_callback("Window moved successfully.")
    else:
        update_callback("No MU window selected. Exiting script.")
