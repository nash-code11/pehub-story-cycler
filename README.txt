===============================================
PEHub Story Cycler - Setup Instructions
===============================================

This tool automatically cycles through the top stories on pehub.com,
displaying each article for 45 seconds and scrolling through the content.


FOR MAC USERS
-------------
1. Unzip "PEHub-Story-Cycler-Mac.zip"
2. Double-click "PEHub-Story-Cycler.app" to run
3. If Mac says "unidentified developer":
   - Right-click the app
   - Click "Open"
   - Click "Open" again in the popup
4. Make sure Chrome is installed

That's it! The app will open Chrome and start cycling through stories.


FOR WINDOWS USERS
-----------------
Step 1: Install Python
   - Go to https://www.python.org/downloads/
   - Download and run the installer
   - IMPORTANT: Check the box "Add Python to PATH" during installation

Step 2: Install required packages
   - Open Command Prompt (search "cmd" in Start menu)
   - Copy and paste this command, then press Enter:

     pip install selenium webdriver-manager

Step 3: Run the script
   - Save "story-cycler.py" to a folder (e.g., Desktop)
   - Open Command Prompt
   - Navigate to that folder:

     cd Desktop

   - Run the script:

     python story-cycler.py

   - Chrome will open and start cycling through stories


OPTIONAL: Create a Windows executable (no Python needed to run)
   - After completing Steps 1 and 2 above, also run:

     pip install pyinstaller

   - Then build the executable:

     pyinstaller --onefile --name "PEHub-Story-Cycler" story-cycler.py

   - The executable will be in the "dist" folder
   - Share "PEHub-Story-Cycler.exe" - recipients just double-click to run


CONTROLS
--------
- Press Ctrl+C in the terminal/command prompt to stop
- The script loops forever by default


TROUBLESHOOTING
---------------
- "Chrome not found": Make sure Google Chrome is installed
- "Permission denied" on Mac: Right-click > Open (see Mac instructions above)
- Script won't start on Windows: Make sure you checked "Add to PATH" when installing Python


===============================================
