import time
from PIL import ImageGrab
import sys

# Wait for page to fully load
time.sleep(3)

# Capture full screen
screenshot = ImageGrab.grab()
screenshot_path = "screenshot.png"
screenshot.save(screenshot_path)
print("Screenshot saved to " + screenshot_path)
print("Size: " + str(screenshot.size))
