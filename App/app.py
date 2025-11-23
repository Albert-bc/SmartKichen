import tkinter as tk
from tkinter import font, PhotoImage
import pyautogui
from gestureRecognitionClass import GestureRecognition
from collections import deque
import subprocess
import threading
import os
import time
from timer_app import TimerApp
import webbrowser
from PIL import Image, ImageTk


# Mapping of gesture names to their corresponding actions
ACTION_NAME_MAP = {
    "OPEN": "Open the dashboard.",
    "6": "Open the music.",
    "8": "Open the document.",
    "UP": "Up operation.",
    "DOWN": "Down operation.",
    "LEFT": "Left operation.",
    "RIGHT": "Right operation."
}



# Gesture operation name
def get_operation_from_action(action, scene):
    if action == "OPEN":
        return "Open the dashboard."
    elif action == "3":
        return "Open the music."
    elif action == "8":
        return "Open the recipe site"
    elif action == "UP":
        if scene == "MUSIC":
            return "Turn up the volume"
        elif scene == "COOK":
            return "Page up"
        elif scene == "TIMER":
            return "Add 30s"
    elif action == "DOWN":
        if scene == "MUSIC":
            return "Turn down the volume"
        elif scene == "COOK":
            return "Page down"
        elif scene == "TIMER":
            return "Subtract 30s"
    elif action == "6":
        if scene == "MUSIC":
            return "Pause/play the music"
        elif scene == "TIMER":
            return "Pause/resume the timer"
        elif scene == "COOK":
            return "Open link"
    elif action == "LEFT":
        if scene == "MUSIC":
            return "Previous music"
        elif scene == "COOK":
            return "Prev element"
        elif scene == "TIMER":
            return "Subtract 30 seconds"
    elif action == "RIGHT":
        if scene == "MUSIC":
            return "Next music"
        elif scene == "COOK":
            return "Next element"
        elif scene == "TIMER":
            return "Add 30 seconds"
    return ""


# the method to control the timer
def control_timer(action, timer):
    if action == "UP" or action == "RIGHT":
        timer.add_time()
    elif action == "6":
        pyautogui.press("enter")
        timer.start_pause_timer()
    elif action == "DOWN" or action == "LEFT":
        timer.subtract_time()

# open groovy music
def open_music():
    subprocess.run("start mswindowsmusic:", shell=True)


# control the music player
def control_media_player(action):
    try:
        if action == "3":
            pyautogui.press('playpause')
        elif action == "RIGHT":
            pyautogui.press('nexttrack')
        elif action == "LEFT":
            pyautogui.press('prevtrack')
        elif action == "3":
            pyautogui.press('playpause')
        elif action == "UP":
            pyautogui.press("volumeup")
        elif action == "DOWN":
            pyautogui.press("volumedown")
        else:
            print(f"Unknown action: {action}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# control cook
def control_cook(action):
    time.sleep(0.5)

    if action == "UP":
        pyautogui.press('up')
    elif action == "DOWN":
        pyautogui.press('down')
    elif action == "LEFT":
        pyautogui.hotkey('shift', 'tab')
    elif action == "RIGHT":
        pyautogui.press("tab")
    elif action == "6":
        pyautogui.press("enter")
    else:
        print("Invalid action")

# open file
def open_file(file_name):
    current_path = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(current_path, file_name)

    # check if file exist
    if os.path.isfile(file_path):
        # open file by default method
        subprocess.run(["start", file_path], shell=True)
    else:
        print(f"No such file: '{file_path}'")


# open recipe site
def open_recipe_site():
    webbrowser.open("https://www.allrecipes.com/")


class WelcomeFrame(tk.Frame):
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.create_widgets()

    def create_widgets(self):
        # Load and resize the image
        original_image = Image.open("welcome.png")
        resized_image = original_image.resize((900, 615), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        label = tk.Label(self, image=self.photo)
        label.pack(pady=20)

        start_btn = tk.Button(self, text="Click me to start using", command=self.start_app, font=("Arial", 18))
        start_btn.pack(pady=20)

    def start_app(self):
        if self.callback:
            self.callback()  # This will switch to the GestureApp frame
        self.pack_forget()


class DashboardFrame(tk.Frame):
    def __init__(self, master=None, back_callback=None):
        super().__init__(master)
        self.master = master
        self.back_callback = back_callback

        # UI
        # Font Styles
        self.header_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.text_font = font.Font(family="Arial", size=12)

        # Adding Labels
        self.scene = "DASHBOARD"
        self.header_label = tk.Label(self, text="DASHBOARD", bg='lightblue', fg='darkblue', font=self.header_font)
        self.header_label.pack(pady=10)

        self.configure(bg='lightblue')

        self.labels = []

    # Update the display labels based on the current gesture stack
    def update_labels(self, stack):
        for i in range(len(self.labels)):
            new_text = f"{get_operation_from_action(stack[i], self.scene)} "
            self.labels[i].config(text=new_text)  # update the label

    def update_header(self, new_header):
        if hasattr(self, "header_label"):
            self.header_label.config(text=new_header)
        else:
            self.header_label = tk.Label(self, text="DASHBOARD", bg='lightblue', fg='darkblue', font=self.header_font)
            self.header_label.pack(pady=10)

    def back_to_welcome(self):
        if self.back_callback:
            self.back_callback()  # This will switch back to the WelcomeFrame
        self.pack_forget()


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gesture Recognition App")
        self.geometry("1000x800")

        self.welcome_frame = WelcomeFrame(self, self.switch_to_gesture_app)
        self.dashboard_frame = DashboardFrame(self, self.switch_to_welcome_frame)

        self.is_welcome_frame = True
        self.scene = "DASHBOARD"

        self.gesture_thread = None

        default_value = ""
        self.gesture_stack = deque([default_value] * 5, maxlen=5)

        self.timer_app = None

        self.last_gesture_time = time.time()
        self.check_for_inactivity()

        # Initially pack the welcome frame
        self.welcome_frame.pack(expand=True, fill=tk.BOTH)

    def switch_to_gesture_app(self):
        self.last_gesture_time = time.time()
        self.welcome_frame.pack_forget()
        self.geometry("400x300")
        self.dashboard_frame.pack(expand=True, fill=tk.BOTH)
        self.is_welcome_frame = False

        if self.gesture_thread == None:
            self.gesture_thread = GestureRecognition(callback=self.callback)
            self.gesture_thread.start()

    def switch_to_welcome_frame(self):
        self.last_gesture_time = time.time()
        self.dashboard_frame.pack_forget()
        self.geometry("1000x800")
        self.welcome_frame.pack(expand=True, fill=tk.BOTH)
        self.is_welcome_frame = True

    # Periodically check if the user has been inactive for a set duration (e.g., 10 seconds)
    def check_for_inactivity(self):
        # Update the last recorded gesture time
        current_time = time.time()
        if current_time - self.last_gesture_time >= 25:
            self.bring_to_front()
            self.switch_to_welcome_frame()

        self.after(1000, self.check_for_inactivity)  # Check again after 5 second

    # Make the app window come to the foreground
    def bring_to_front(self):
        self.attributes('-topmost', True)  # Bring to front
        self.after_idle(self.attributes, '-topmost', False)  # Disable always-on-top after window is raised

    def set_scene(self, new_scene):
        self.dashboard_frame.update_header(new_scene)
        self.scene = new_scene

    # Based on the gesture and scene, perform the corresponding action
    def callback(self, now):
        if self.is_welcome_frame:  # if WelcomeFrame is active, ignore main app operations
            return

        self.last_gesture_time = time.time()  # Update the last gesture time when a new gesture is detected

        print(now)
        last = self.gesture_stack[-1]
        self.gesture_stack.append(now)
        print("-1", self.gesture_stack[-1], "-2", self.gesture_stack[-2], self.gesture_stack)
        if now == "OPEN" and last == "OK":
            self.gesture_stack.append("")
            self.bring_to_front()
            self.set_scene("DASHBOARD")
        elif now == "2":
            self.set_scene("TIMER")
            self.gesture_stack.append("")
            if not self.timer_app:
                self.timer_app = TimerApp()
            else:
                # Show the timer window if it was previously hidden
                self.timer_app.deiconify()
        elif now == "3":
            self.set_scene("MUSIC")
            open_music()
        elif now == "8":
            if self.scene == "COOK":
                return
            else:
                self.set_scene("COOK")
                open_recipe_site()
                time.sleep(1)
                # do 20 times tab key press to skip the menu links
                for i in range(20):
                    pyautogui.press("tab")
        else:
            if self.scene == "MUSIC":
                control_media_player(now)
            elif self.scene == "COOK":
                control_cook(now)
            elif self.scene == "TIMER":
                control_timer(now, self.timer_app)
        self.dashboard_frame.update_labels(self.gesture_stack)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
