# 3D Save Reminder Daemon (Visual Edition)

A lightweight, zero-overhead background utility designed for 3D artists and animators. It monitors active rendering software and enforces saving discipline through a "visual hostage" mechanic. 

Instead of jarring audio alarms, this daemon quietly monitors your session. If 25 minutes pass without a save, it overlays a translucent, persistent quote on your screen. The quote cannot be clicked away or dismissed—it locks on screen until you physically press `Ctrl+S`.

## Features
* **Visual Hostage Mechanic:** Subtitles remain stubbornly on top of all windows until you save.
* **Targeted Monitoring:** Only tracks time when target applications (Blender, Maya, ZBrush, Unreal Engine) are actively running.
* **Zero Terminal Footprint:** Runs completely invisibly in the Windows background.
* **Instant Kill Switch:** Hardcoded `Ctrl + Alt + Q` global shortcut to immediately terminate the daemon when you clock out.

## Supported Software
By default, the daemon monitors:
* Blender (`blender.exe`)
* Autodesk Maya (`maya.exe`)
* ZBrush (`zbrush.exe`)
* Unreal Engine 5 (`unrealeditor.exe`)

*(You can add more applications by editing the `TARGET_APPS` list in `daemon.py`).*

## Customizing the Timer
By default, the reminder triggers after 25 minutes of active, unsaved work. To change this interval before building your own executable:

1. Open `daemon.py` in any text editor.
2. Scroll to the very bottom of the script and locate the `if __name__ == "__main__":` block.
3. Modify the `REMINDER_INTERVAL` variable to your preferred time in seconds. For example, to set a 30-minute timer, update it to:
   ```python
   REMINDER_INTERVAL = 30 * 60

```

4. Save the file and proceed with the PyInstaller build instructions below.

## How to Use (For Artists)

1. Download the latest `daemon.exe` from the Releases page.
2. Double-click the file. It will prompt for Administrator privileges (required for global keyboard hooks).
3. The daemon is now running silently. Open your 3D software and work normally.
4. When the visual quote appears, press `Ctrl + S` to save your work and dismiss the overlay.
5. When you are done for the day, press `Ctrl + Alt + Q` to kill the background process.

## How to Build from Source

Building this daemon requires a native Windows Python environment to correctly compile the OS-level keyboard hooks.

1. Clone the repository to a native Windows directory (do not build across a WSL network share).
2. Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```


3. Install the dependencies:
```powershell
pip install -r requirements.txt
pip install pyinstaller

```


4. Compile the standalone executable with UAC Admin elevation and no console:
```powershell
pyinstaller --noconsole --onefile --uac-admin --clean daemon.py

```


5. The final standalone executable will be located in the `dist/` folder.

```

Once you hit enter, the file will be created and you are ready to run your `git add .`, `git commit`, and `git push` commands.

```
