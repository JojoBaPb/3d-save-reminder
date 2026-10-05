import os
import time
import logging
import subprocess
import random
import threading
import psutil
import keyboard
import tkinter as tk

# Basic logging to monitor state changes in the terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

TARGET_APPS = [
    "blender", "blender.exe",
    "zbrush.exe",
    "maya", "maya.exe",
    "unrealeditor", "unrealeditor.exe"
]

REMINDER_INTERVAL = 45 * 60
POLL_INTERVAL = 10  

# Jim Rohn-inspired save quotes
QUOTES = [
    "Discipline is the bridge between a masterpiece and a crash to desktop. Save your work.",
    "We must all suffer one of two things: the pain of discipline or the pain of lost progress.",
    "Success is nothing more than a few simple disciplines, practiced every day. Hit Ctrl+S.",
    "You cannot change your destination overnight, but you can change your save habits immediately.",
    "Don't let hours of rendering become a tragedy of negligence. Save now."
]

def is_app_running(app_list):
    """Iterate through active processes, suppressing subprocess terminal windows."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in app_list:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    try:
        # 0x08000000 is the Windows API flag for CREATE_NO_WINDOW
        # Using absolute path prevents PATH hijacking vulnerabilities
        output = subprocess.check_output(
            ["C:\\Windows\\System32\\tasklist.exe", "/FO", "CSV"], 
            creationflags=0x08000000
        ).decode("utf-8", errors="ignore").lower()
        
        for app in app_list:
            if app in output:
                return True
    except FileNotFoundError:
        pass

    return False

def _display_subtitle(quote, saved_event):
    """Renders the Tkinter window and keeps it alive until the saved_event is triggered."""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    chroma_key = '#000001'
    root.configure(bg=chroma_key)
    try:
        root.attributes("-transparentcolor", chroma_key)
    except tk.TclError:
        pass 

    root.attributes("-alpha", 0.0) 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    label = tk.Label(
        root,
        text=quote,
        font=("Helvetica", 24, "bold"),
        fg="white",
        bg=chroma_key,
        wraplength=screen_width - 200,
        justify="center"
    )
    label.pack(pady=10)

    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = (screen_width // 2) - (window_width // 2)
    y = screen_height - window_height - 150 
    root.geometry(f"+{x}+{y}")

    # Fade in
    for i in range(1, 11):
        if saved_event.is_set():
            break
        root.attributes("-alpha", i / 10.0)
        root.update()
        time.sleep(0.05)

    # Hold indefinitely on screen until Ctrl+S is pressed
    while not saved_event.is_set():
        time.sleep(0.1)
        try:
            root.update()
        except tk.TclError:
            break  # Break if window was forcefully closed

    # Fade out rapidly upon saving
    for i in range(9, -1, -2):
        try:
            root.attributes("-alpha", i / 10.0)
            root.update()
        except tk.TclError:
            break
        time.sleep(0.05)

    try:
        root.destroy()
    except tk.TclError:
        pass

def trigger_reminder():
    """Triggers the visual quote and waits for Ctrl+S to dismiss it."""
    quote_text = random.choice(QUOTES)
    logging.info(f"EVENT TRIGGERED: Displaying quote. Waiting for Ctrl+S...")
    
    # Event flag to communicate between the hotkey listener and the Tkinter thread
    saved_event = threading.Event()

    def on_save():
        if not saved_event.is_set():
            logging.info("Saved! Subtitle cleared.")
            saved_event.set()
            try:
                keyboard.remove_hotkey('ctrl+s')
            except KeyError:
                pass

    # Register the global hotkey
    keyboard.add_hotkey('ctrl+s', on_save)

    # Spawn the visual window
    threading.Thread(target=_display_subtitle, args=(quote_text, saved_event), daemon=True).start()

    # Block the main timer thread until they save
    while not saved_event.is_set():
        time.sleep(0.1)

def main():
    logging.info("3D Save Reminder (Visual Edition) Started. Monitoring...")
    active_session_time = 0

    keyboard.add_hotkey('ctrl+alt+q', lambda: os._exit(0))

    while True:
        if is_app_running(TARGET_APPS):
            active_session_time += POLL_INTERVAL
            logging.info(f"Target app active. Unsaved time: {active_session_time}s")

            if active_session_time >= REMINDER_INTERVAL:
                trigger_reminder()
                # Timer remains frozen until trigger_reminder() unblocks via Ctrl+S
                active_session_time = 0
        else:
            if active_session_time > 0:
                logging.info("Target app closed. Timer reset.")
            active_session_time = 0

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    # Temporarily override the interval to 10 seconds for rapid testing
    REMINDER_INTERVAL = 25 * 60
    main()
