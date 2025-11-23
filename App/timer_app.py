import tkinter as tk
from tkinter import font
from tkinter import messagebox

class TimerApp(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Timer")
        self.geometry("450x150")

        self.time_left = tk.IntVar(value=0)
        self.running = False

        # Display
        self.timer_display = tk.Label(self, textvariable=self.time_left, font=("Arial", 20))
        self.timer_display.pack(pady=20)

        # Buttons
        self.start_pause_button = tk.Button(self, text="Start/Pause", command=self.start_pause_timer)
        self.start_pause_button.pack(pady=5, padx=10, side="left")

        self.add_button = tk.Button(self, text="Add 30s", command=self.add_time)
        self.add_button.pack(pady=5, padx=10, side="left")

        self.subtract_button = tk.Button(self, text="Subtract 30s", command=self.subtract_time)
        self.subtract_button.pack(pady=5, padx=10, side="left")

        self.update_timer()

    def update_timer(self):
        if self.running and self.time_left.get() > 0:
            self.time_left.set(self.time_left.get() - 1)
            self.after(1000, self.update_timer)
        elif self.time_left.get() == 0 and self.running:
            self.running = False
            tk.messagebox.showinfo("Timer", "Time's up!")
            self.withdraw()  # Hide the window

    def start_pause_timer(self):
        if self.time_left.get() > 0:
            self.running = not self.running
            if self.running:
                self.update_timer()

    def add_time(self):
        self.time_left.set(self.time_left.get() + 30)

    def subtract_time(self):
        new_time = self.time_left.get() - 30
        if new_time < 0:
            new_time = 0
        self.time_left.set(new_time)
