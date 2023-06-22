import pytesseract
import pyautogui
import hashlib
import cv2
import numpy as np
from PIL import Image, ImageEnhance

# Add the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# List of blacklisted names
blacklist = ['Touch']
blacklist.append('slaw')
blacklist.append('Daddy')
# Stores the hash of the previous screenshot
prev_hash = None

lower = (95,150,204) 
upper = (100,160,255)

while True:
    # Capture screenshot from primary monitor
    screenshot = pyautogui.screenshot()

    # Compute the hash of the current screenshot
    curr_hash = hashlib.sha256(screenshot.tobytes()).hexdigest()

    if curr_hash != prev_hash:
        prev_hash = curr_hash  # Update the hash for the next round
        print("Screen changed!")

        # Convert PIL Image to OpenCV format
        screenshot_cv = np.array(screenshot)
        screenshot_cv = screenshot_cv[:, :, ::-1].copy()

        # Convert the image to HSV
        hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)

        # Create a mask that only includes pixels within the color range
        mask = cv2.inRange(hsv, np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8))

        # Apply the mask to the image
        filtered = cv2.bitwise_and(screenshot_cv, screenshot_cv, mask=mask)

        # Convert the filtered image back to PIL format
        screenshot_filtered = Image.fromarray(cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB))

        # Convert the image to grayscale and enhance contrast for better OCR
        screenshot_filtered = screenshot_filtered.convert('L')
        screenshot_filtered = ImageEnhance.Contrast(screenshot_filtered).enhance(2.0)

        # Get text from screenshot
        data = pytesseract.image_to_data(screenshot_filtered, output_type=pytesseract.Output.DICT, config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

        for name in blacklist:
            for i, txt in enumerate(data['text']):
                if name in txt:
                    print("Text found!")
                    print("All text on screen: ", ' '.join(data['text']))
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    pyautogui.rightClick(x + w / 2, y + h / 2)
                    # Given the kick option is 78 pixels down and 37 pixels to the right of the right click position
                    pyautogui.click(x + w / 2 + 37, y + h / 2 + 78)
