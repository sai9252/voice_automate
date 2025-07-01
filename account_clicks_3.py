import pyautogui
import time

print("Starting automation in 5 seconds...")
print("Please switch to the target window/application.")
time.sleep(1)  # Give yourself time to switch to the target window

pyautogui.FAILSAFE = True  # Enable Failsafe: move mouse to top-left corner to stop

# Values from the image
coordinates = [
    (805, 304),
    (563, 420),
    (665, 761),
    (642, 864),
    (576, 958),
    (577, 1070),
    (638, 712)
]

for i in range(100):
    print(f"\n--- Iteration {i+1} ---")
    
    for j, (x, y) in enumerate(coordinates):
        pyautogui.scroll(-500)  # Scroll down
        print(f"Iteration {i+1}: Move to ({x}, {y}) and click")
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
    
    time.sleep(3)  # Wait before next iteration

print("\nAutomation script finished.")
