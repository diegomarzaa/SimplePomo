import tkinter as tk
from tkinter import messagebox, simpledialog, Scale
import pygame
import threading
import os
import sys

os.environ['PYGAME_DETECT_AVX2'] = '1'

# CONSTANTS
WINDOW_WIDTH = 105
WINDOW_HEIGHT = 90

BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#ff6347"

TIMER_FONT_SIZE = 15
TIMER_FONT = ("Helvetica", TIMER_FONT_SIZE, "bold")

BUTTON_FONT = ("Helvetica", 10)

DEFAULT_POMODORO_TIME = 25 * 60  # Default time in seconds (25 minutes)
POMODORO_STEP = 60

class PomodoroTimer:
    def __init__(self, initial_time=None):
        self.root = tk.Tk()
        self.root.title("")

        self.setup_main_window()

        self.running = False
        self.time_left = initial_time if initial_time else DEFAULT_POMODORO_TIME
        self.after_id = None
        self.volume = 50  # Default volume (0-100)

        self.create_widgets()

        self.root.bind('<Return>', lambda event: self.toggle_timer())
        self.root.bind('<space>', lambda event: self.on_settings_click())
        self.root.bind('<q>', lambda event: self.root.destroy())

        pygame.mixer.init()

        if initial_time:
            self.start_timer()

    def setup_main_window(self):
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()
        position_top = int(screen_height - WINDOW_HEIGHT)
        position_right = int(screen_width - WINDOW_WIDTH / 2)

        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{position_right}+{position_top}')
        self.root.config(bg=BG_COLOR)
        self.root.lift()
        self.root.attributes("-topmost", True, '-alpha', 0.85)
        self.root.overrideredirect(True)
  
    def adjust_duration(self, change):
        new_time = self.time_left + change * 60
        if 60 <= new_time <= 7200:  # Limit between 1 minute and 2 hours
            self.time_left = new_time
            if not self.running:
                global DEFAULT_POMODORO_TIME
                DEFAULT_POMODORO_TIME = self.time_left
            self.update_timer_label()

    def create_widgets(self):
        # Timer frame
        timer_frame = tk.Frame(self.root, bg=BG_COLOR)
        timer_frame.pack(expand=True)

        # Decrease time button
        self.decrease_button = tk.Button(
            timer_frame,
            text="−",
            font=("Helvetica", 5),
            width=1,
            height=1,
            border=0,
            padx=1,  # Remove internal padding
            pady=1,
            borderwidth=0,
            bg=BG_COLOR,
            fg=FG_COLOR,
            command=lambda: self.adjust_duration(-5)
        )
        self.decrease_button.pack(side=tk.LEFT)

        # Timer label
        self.timer_label = tk.Label(
            timer_frame, 
            text=self.format_time(self.time_left),
            font=TIMER_FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        self.timer_label.pack(side=tk.LEFT, padx=5)
        self.timer_label.bind("<Button-1>", self.on_settings_click)

        # Increase time button
        self.increase_button = tk.Button(
            timer_frame,
            text="+",
            font=("Helvetica", 5),
            width=1,
            height=1,
            borderwidth=0,
            padx=1,  # Remove internal padding
            pady=1,
            border=0,
            bg=BG_COLOR,
            fg=FG_COLOR,
            command=lambda: self.adjust_duration(5)
        )
        self.increase_button.pack(side=tk.LEFT)

        # Control buttons frame
        frame_controls = tk.Frame(self.root, bg=BG_COLOR)
        frame_controls.pack(fill=tk.BOTH, expand=True)

        # Play/Pause button
        self.run_pause_button = tk.Button(
            frame_controls,
            font=BUTTON_FONT,
            text="▶",
            border=0,
            bg=BG_COLOR,
            fg=FG_COLOR,
            activebackground=ACCENT_COLOR,
            command=self.toggle_timer
        )
        self.run_pause_button.pack(side=tk.LEFT, expand=True)

        # Stop button
        self.stop_button = tk.Button(
            frame_controls,
            font=BUTTON_FONT,
            text="■",
            border=-1,
            bg=BG_COLOR,
            fg=FG_COLOR,
            command=self.stop_timer
        )
        self.stop_button.pack(side=tk.RIGHT, expand=True)

        # Volume bar
        self.volume_scale = Scale(
            self.root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.update_volume,
            length=WINDOW_WIDTH - 10,
            bg=BG_COLOR,
            fg=BG_COLOR,
            highlightthickness=0,
            sliderrelief=tk.FLAT,
            showvalue=0,
            troughcolor=BG_COLOR,
            sliderlength=20,
        )
        self.volume_scale.set(self.volume)
        self.volume_scale.pack(side=tk.BOTTOM, pady=(0, 5))

    def toggle_timer(self, event=None):
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        threading.Thread(target=self.play_sound, args=("sounds/rain.mp3",), daemon=True).start()
        self.running = True
        self.run_pause_button.config(text="||", bg=BG_COLOR, fg=FG_COLOR)
        if not self.after_id:
            self.countdown()

    def pause_timer(self):
        self.stop_sound()
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.running = False
        self.run_pause_button.config(text="▶", bg=BG_COLOR, fg=FG_COLOR)

    def stop_timer(self):
        self.pause_timer()
        self.time_left = DEFAULT_POMODORO_TIME
        self.update_timer_label()

    def countdown(self):
        if self.running:
            if self.time_left > 0:
                self.time_left -= 1
                self.update_timer_label()
                self.after_id = self.root.after(1000, self.countdown)
            else:
                self.end_timer()

    def end_timer(self):
        threading.Thread(target=self.play_sound, args=("sounds/end.mp3", False), daemon=True).start()
        self.running = False
        messagebox.showinfo("Timer", "Time's up!")
        self.stop_timer()

    def update_timer_label(self):
        self.timer_label.configure(text=self.format_time(self.time_left))

    def format_time(self, total_seconds):
        minutes, seconds = divmod(total_seconds, 60)
        return f'{minutes:02d}:{seconds:02d}'
    
    def on_settings_click(self, event=None):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry(f"300x150+{self.root.winfo_x()}+{self.root.winfo_y()}")

        tk.Label(settings_window, text="Pomodoro duration (minutes):").pack()
        duration_entry = tk.Entry(settings_window)
        duration_entry.insert(0, str(DEFAULT_POMODORO_TIME // 60))
        duration_entry.pack()
        duration_entry.focus_set()  # Focus the entry for immediate typing
        
        # Bind Enter key to apply settings immediately
        duration_entry.bind('<Return>', lambda event: self.apply_settings(duration_entry.get(), settings_window))
        
        tk.Button(settings_window, text="Apply", command=lambda: self.apply_settings(duration_entry.get(), settings_window)).pack()

    def apply_settings(self, duration, window):
        try:
            mins = int(duration)
            if 1 <= mins <= 120:
                self.update_pomodoro_time(mins)
            else:
                messagebox.showerror("Error", "Duration must be between 1 and 120 minutes.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for duration.")
        window.destroy()

    def update_volume(self, value):
        self.volume = int(self.volume_scale.get())
        pygame.mixer.music.set_volume(self.volume / 100)

    def play_sound(self, file_path, loop=True):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, file_path)
        
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(self.volume / 100)
        if loop:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()

    def stop_sound(self):
        pygame.mixer.music.stop()

    def update_pomodoro_time(self, mins):
        global DEFAULT_POMODORO_TIME
        DEFAULT_POMODORO_TIME = mins * POMODORO_STEP
        if not self.running:
            self.time_left = DEFAULT_POMODORO_TIME
            self.update_timer_label()
    
    def run(self):
        self.root.mainloop()

def main():
    initial_time = None
    if len(sys.argv) > 1:
        try:
            initial_time = int(sys.argv[1]) * 60
        except ValueError:
            print("Invalid argument. Please provide a valid number of minutes.")
            sys.exit(1)
    
    PomodoroTimer(initial_time).run()

if __name__ == "__main__":
    main()

