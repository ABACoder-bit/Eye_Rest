import tkinter as tk
import keyboard
import winsound
import sys
import os
import threading
import time
from pycaw.pycaw import AudioUtilities
import pystray
from PIL import Image, ImageDraw

# --- FINAL PRODUCTION TIMINGS (Milliseconds) ---
WORK_DURATION = 20 * 60 * 1000     # 20 minutes
BREAK_DURATION = 60 * 1000         # 40 seconds total break
MID_BREAK_TIME = 30 * 1000         # 20 seconds into the break

# WORK_DURATION = 20 * 1000      # 20 seconds
# BREAK_DURATION = 10 * 1000     # 10 seconds total break
# MID_BREAK_TIME = 5 * 1000      # 5 seconds into the break

KILL_SHORTCUT = 'ctrl+shift+q'
SKIP_SHORTCUT = 'ctrl+shift+s'

# Fix the path issue so the .pyw file can always find the audio file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(SCRIPT_DIR, 'Airplane_chime.wav')

def is_audio_playing():
    """Checks if any application is actively outputting audio."""
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.State == 1:
                return True
        return False
    except Exception as e:
        return False

def create_tray_image():
    """Dynamically draws a green circle for the system tray icon."""
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill=(0, 255, 0))
    return image

class EyeCareTimer:
    def __init__(self, root):
        self.root = root
        self.resume_audio_after_break = False
        self.in_break = False
        self.scheduled_events = []
        
        # Time tracking for sleep detection
        self.work_start_time = 0
        self.last_tick_time = 0
        
        # Configure the black window
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black', cursor="none")
        self.root.withdraw()
        
        # Global hotkeys
        keyboard.add_hotkey(KILL_SHORTCUT, self.terminate_program)
        keyboard.add_hotkey(SKIP_SHORTCUT, self.skip_break)
        
        # Setup System Tray Icon
        menu = pystray.Menu(pystray.MenuItem('Quit Timer', self.quit_from_tray))
        self.tray_icon = pystray.Icon("EyeTimer", create_tray_image(), "20-20-20 Eye Timer", menu)
        
        # Run the tray icon in a background thread so it doesn't freeze Tkinter
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        
        self.start_work_phase()

    def quit_from_tray(self, icon, item):
        icon.stop()
        self.root.after(0, self.terminate_program)

    def schedule_event(self, ms, func, *args):
        event_id = self.root.after(ms, func, *args)
        self.scheduled_events.append(event_id)
        return event_id

    def cancel_all_events(self):
        for event_id in self.scheduled_events:
            self.root.after_cancel(event_id)
        self.scheduled_events.clear()

    def play_airplane_chime(self):
        if os.path.exists(AUDIO_FILE):
            winsound.PlaySound(AUDIO_FILE, winsound.SND_FILENAME | winsound.SND_NODEFAULT)

    def toggle_media(self):
        keyboard.send('play/pause media')

    def start_work_phase(self):
        self.in_break = False
        self.cancel_all_events()
        self.root.withdraw() 
        
        # Initialize time tracking for this work block
        self.work_start_time = time.time()
        self.last_tick_time = time.time()
        
        # Start the 1-second background tick
        self.check_work_progress()

    def check_work_progress(self):
        """Checks the time every second to detect sleep and trigger breaks."""
        self.scheduled_events.clear() # Keeps memory clean
        
        current_time = time.time()
        
        # SLEEP DETECTION: If more than 10 seconds passed since the last tick, the PC slept
        if current_time - self.last_tick_time > 10:
            print("System sleep detected. Resetting work timer.")
            self.work_start_time = current_time
            
        self.last_tick_time = current_time
        
        # Convert elapsed seconds to milliseconds to compare with WORK_DURATION
        elapsed_ms = (current_time - self.work_start_time) * 1000
        
        if elapsed_ms >= WORK_DURATION:
            self.start_break_phase()
        else:
            # Tick again in 1 second (1000 ms)
            self.schedule_event(1000, self.check_work_progress)

    def start_break_phase(self):
        self.in_break = True
        
        self.resume_audio_after_break = is_audio_playing()
        
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        if self.resume_audio_after_break:
            self.schedule_event(300, self.toggle_media)
            
        self.schedule_event(MID_BREAK_TIME, self.mid_break_action)

    def mid_break_action(self):
        self.play_airplane_chime()
        remaining_time = BREAK_DURATION - MID_BREAK_TIME
        self.schedule_event(remaining_time, self.end_break_phase)

    def end_break_phase(self):
        self.play_airplane_chime()
        self.root.withdraw() 
        
        if self.resume_audio_after_break:
            self.schedule_event(300, self.toggle_media)
            
        self.start_work_phase()

    def skip_break(self):
        if self.in_break:
            self.root.after(0, self._execute_skip)
        else:
            self.root.after(0, self.start_work_phase)

    def _execute_skip(self):
        self.cancel_all_events()
        self.root.withdraw()
        
        if self.resume_audio_after_break:
            self.toggle_media()
            self.resume_audio_after_break = False
            
        self.start_work_phase()

    def terminate_program(self):
        self.cancel_all_events()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeCareTimer(root)
    root.mainloop()