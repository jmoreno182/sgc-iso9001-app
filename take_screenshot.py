from PIL import ImageGrab
import time

time.sleep(2)
screenshot = ImageGrab.grab()
screenshot.save("streamlit_screenshot.png")
print("Saved streamlit_screenshot.png")
