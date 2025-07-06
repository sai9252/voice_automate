# from pathlib import Path
# import os

# directory_path = r"C:\Users\M sai\Downloads"


# audio_extensions = ['.mp3']
# audio_files = []

# directory = Path(directory_path)
# if not directory.exists():
#     raise FileNotFoundError(f"Directory not found: {directory_path}")

# first_audio_files = [i for i in directory.glob("*.mp3")][0]
# # print(f"Found {len(all_audio_files)} audio files in directory: {directory_path}")
# print("Audio file:", first_audio_files)
# print(first_audio_files.suffix)
# print(first_audio_files.stat())
# print(first_audio_files)


# for ext in audio_extensions:
#     audio_files.extend(directory.glob(f"*{ext}"))
#     audio_files.extend(directory.glob(f"*{ext.upper()}"))

# if not audio_files:
#     raise FileNotFoundError(f"No audio files found in directory: {directory_path}")

# # Sort files for consistent ordering
# audio_files.sort()
import pyautogui
import time
from datetime import datetime
import os

class AutomationBot:
    def __init__(self):
        # Define the screen position to monitor
        self.pixel_position = (1245, 460)  # Change this to the position of your green button
        self.check_interval = 2  # Seconds to wait before retrying

        # Create folder to store screenshots
        self.screenshot_folder = "screenshots"
        os.makedirs(self.screenshot_folder, exist_ok=True)

    def is_green(self, rgb, tolerance=30):
        """Check if the color is green based on RGB and tolerance."""
        r, g, b = rgb
        print(f"🔍 Comparing R: {r}, G: {g}, B: {b} with tolerance: {tolerance}")
        is_green_result = (
            g > r + tolerance and
            g > b + tolerance and
            g > 100
        )
        print(f"🧪 Green detection result: {is_green_result}")
        return is_green_result

    def save_screenshot(self, image):
        """Save the screenshot with a timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshot_folder, filename)
        image.save(filepath)
        print(f"🖼 Screenshot saved: {filepath}")

    def monitor_pixel_and_act(self):
        """Monitor a pixel and trigger automation if green is detected."""
        print("👀 Monitoring pixel for green color...")

        while True:
            # Take a screenshot
            screenshot = pyautogui.screenshot()

            # Save the screenshot
            self.save_screenshot(screenshot)

            # Get pixel color
            pixel_color = screenshot.getpixel(self.pixel_position)
            print(f"🎯 Pixel color at {self.pixel_position}: {pixel_color}")

            # Check if the pixel is green
            if self.is_green(pixel_color):
                print("✅ Green color detected! Running main automation sequence...")
                self.main_automation_sequence()
                break  # Exit the loop after executing the automation
            else:
                print("❌ Green not detected. Retrying after delay...")
                time.sleep(self.check_interval)  # Wait and retry

    def main_automation_sequence(self):
        """Your main task logic goes here."""
        print("🔁 Running main automation sequence...")
        # Example action:
        pyautogui.click(self.pixel_position)
        print("🖱 Clicked on the detected green button.")
        # Add more actions here as needed

# Example usage
if __name__ == "__main__":
    bot = AutomationBot()
    bot.monitor_pixel_and_act()
