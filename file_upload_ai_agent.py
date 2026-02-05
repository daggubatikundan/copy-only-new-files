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

