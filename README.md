# Eye_Rest
A Windows Project to Implement the 20-20-20 Rule with time tracking



A lightweight, background-running Windows utility designed to enforce the 20-20-20 eye care rule: every 20 minutes, look at an object 20 feet away for 20 seconds.
Unlike standard alarm applications, this tool is optimized for deep work. It actively manages system media by detecting active audio streams and pausing them during the break interval. 
The application intentionally does not resume media after the break concludes, serving as a focus checkpoint to help users evaluate if they should return to previous media or remain on task.

Features
Smart Media Management: Uses Windows Audio APIs (pycaw) to detect and pause active audio sessions at the start of a break.
System Sleep Protection: Automatically detects OS sleep or hibernation states and resets the work timer upon waking to prevent immediate interruptions.
Windowless Execution: Operates as a .pyw process, running silently in the background with a near-zero CPU footprint.
System Tray and Taskbar Integration: Includes a dynamically drawn tray icon for visual confirmation of the active process and easy termination.
Global Hotkeys: System-wide shortcuts to bypass active breaks or kill the process without terminal access.
Keyboard Shortcuts

Terminate Application: Ctrl + Shift + Q
Skip Active Break: Ctrl + Shift + S

Configuration Note
The Airplane_chime.wav audio file must be located in the same directory as the script for notification chimes to function correctly.

Installation and Usage
Clone the Repository

cd EyeCareTimer
Install Dependencies
pip install -r requirements.txt

Double-click EyeCareTimer.pyw to launch the timer silently in the background.
