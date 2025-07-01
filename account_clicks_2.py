import pyautogui
import time

print("Starting automation in 5 seconds...")
print("Please switch to the target window/application.")
time.sleep(5)  # Give yourself time to switch to the target window

pyautogui.FAILSAFE = True  # Enable Failsafe: move mouse to top-left corner to stop

# Define all coordinates in a list for better organization
coordinates = [
    (1520,990),
    (946,531),
    (1584,482),
    (955,582),
    (753,890),
    (685,950),
    (642,1015),
    (725,1094),
    (1000,720),
    (1526,761),
    (1040,700),
]

for i in range(1000):
    print(f"\n--- Iteration {i+1} ---")
    
    # pyautogui.hotkey('ctrl', 'r')
    # time.sleep(3)
    for j, (x, y) in enumerate(coordinates):
        pyautogui.scroll(-500)
        print(f"Iteration {i+1}: Move to ({x}, {y}) and click")
        pyautogui.moveTo(x, y,duration=0.2)
        pyautogui.click()
    
    time.sleep(3)  # Wait before next iteration


print("\nAutomation script finished.")
