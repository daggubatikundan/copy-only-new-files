# AI Agent to attach only new files from a network location to the application via browser.
Copy only new files and not the old ones

To build an autonomous AI agent that handles these weekly uploads, we will use **Python**, **Playwright** for web automation, and **Windows Task Scheduler** for the weekly trigger.

While **LangGraph** is excellent for complex decision-making loops, for a deterministic task like "find files and upload them," a structured Playwright script is more reliable and easier to maintain.

### Step 1: Set Up the Environment

1. **Install Python:** Ensure Python 3.8+ is installed.
2. **Install Dependencies:** Open your terminal (PowerShell or CMD) and run:
```bash
pip3 install playwright
playwright install chromium

```



---

### Step 2: The Automation Code (`agent.py`)

This script handles the logic of filtering files by date and performing the browser automation.

```python
import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
NETWORK_LOCATION = r'\\suh-msi-app\ARCHIVE1'  # Use raw string (r) for Windows paths
APP_URL = "https://app.rivethealth.com/..." # Replace with your specific Rivet URL
FILE_EXTENSIONS = ('.835', '.837')

def get_weekly_files(directory):
    """Returns a list of file paths generated in the last 7 days."""
    weekly_files = []
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)

    for filename in os.listdir(directory):
        if filename.endswith(FILE_EXTENSIONS):
            file_path = os.path.join(directory, filename)
            # Get creation time (Windows)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if creation_time > one_week_ago:
                weekly_files.append(file_path)
    
    return weekly_files

def run_agent():
    files_to_upload = get_weekly_files(NETWORK_LOCATION)
    
    if not files_to_upload:
        print("No files found from the last 7 days. Exiting.")
        return

    print(f"Found {len(files_to_upload)} files to upload.")

    with sync_playwright() as p:
        # Launch browser (headless=False lets you see it happen)
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context()
        page = context.new_page()

        # 1. Navigate to the app
        page.goto(APP_URL)
        
        # 2. Click 'Upload claims' 
        # Note: 'has_text' is used to match the specific button
        page.get_by_role("button", name="Upload claims").click()

        # 3. Handle File Chooser
        # Playwright intercepts the OS file dialog
        with page.expect_file_chooser() as fc_info:
             # This click should trigger the system file browse dialog
             page.get_by_label("Browse").click() 
        
        file_chooser = fc_info.value
        file_chooser.set_files(files_to_upload)

        # 4. Submit
        page.get_by_role("button", name="Submit").click()
        
        # Give it a moment to finish the upload before closing
        page.wait_for_timeout(5000) 
        print("Upload complete.")
        browser.close()

if __name__ == "__main__":
    run_agent()

```

---

### Step 3: Schedule Weekly Execution

To make this run every week on your Windows machine:

1. Search for **Task Scheduler** in the Windows Start menu.
2. Click **Create Basic Task** on the right sidebar.
3. **Name:** `RivetWeeklyUpload`.
4. **Trigger:** Select **Weekly**, then choose your day (e.g., Monday at 8:00 AM).
5. **Action:** Select **Start a Program**.
6. **Program/script:** Type `pythonw.exe` (this runs it without a console window) or just `python.exe`.
7. **Add arguments:** Enter the full path to your script, e.g., `"C:\Users\Name\Scripts\agent.py"`.
8. **Start in:** Enter the folder path where the script is located (to ensure relative paths work).

---

### Pro-Tips for Rivet/Web Automation

* **Locators:** If `get_by_role` doesn't find the button, use the **Playwright Inspector** to find the exact selector. Run `npx playwright codegen <URL>` in your terminal to record your clicks and generate the exact code.
* **Headless Mode:** Once you confirm the script works, change `headless=False` to `headless=True` in the code so the browser runs silently in the background.
* **Logging:** If this is for professional use, consider adding a `logging` module to save the results of each run to a text file for auditing.

Would you like me to refine the selectors for the 'Upload' button if you can provide the HTML or a screenshot of that part of the app?

