import pyautogui
import time
import threading
import sys
from ai import analyse_audio_transcript_copy


API_KEYS = ["AIzaSyCtVcmwLzABVykY-1YKwMM66tCwSake-ec","AIzaSyBtVTsFNm0HWiWR8WIwQFHOszNotZpKigs","AIzaSyDlHJayH_4bV1A85fvUhGXmkXD-VVKOfbs","AIzaSyB6woe43tn0-Rprh6hfJ0W1UKDnsnoRZF8","AIzaSyBj6N89c343uCeJci_Px34i8pevUWZLuKc"]


class AutomationBot:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.setup_delay = 1
        self.action_delay = 0.1
        self.reload_delay = 1
        self.pixel_position = (1255, 821)  # Change this to the position of your green button
        self.check_interval = 2
        self.background_results = {}
        self.background_exceptions = {}  # Store exceptions from background tasks
        self.background_threads = []
        self._stop_requested = False 
        self.index = 0 # Flag to stop iterations
        
    def wait(self, seconds=None):
        """Smart wait with default action delay"""
        time.sleep(seconds or self.action_delay)
    
    def click_at(self, x, y, clicks=1, delay=0.5):
        """Move to coordinates and click"""
        pyautogui.moveTo(x, y, duration=delay)
        if clicks == 2:
            pyautogui.doubleClick()
        elif clicks == 3:
            pyautogui.tripleClick()
        else:
            pyautogui.click()
        self.wait()
    
    def hotkey_press(self, *keys):
        """Press hotkey combination"""
        pyautogui.hotkey(*keys)
        self.wait()
    
    def run_background_analysis(self, task_id):
        def background_task():
            print(f"Starting background analysis {task_id}...")
            for i, api_key in enumerate(API_KEYS):
                try:
                    print(f"[{task_id}] Trying API key {i + 1}/{len(API_KEYS)}")
                    result = analyse_audio_transcript_copy(api_key)
                    self.background_results[task_id] = result
                    self.background_exceptions[task_id] = None
                    print(f"[{task_id}] Analysis successful.")
                    return
                except Exception as e:
                    if "RESOURCE_EXHAUSTED" in str(e) or "INVALID_API_KEY" in str(e):
                        print(f"[{task_id}] API key {i + 1} exhausted: {e}")
                        continue
                    else:
                        print(f"[{task_id}] Fatal error: {e}")
                        self.background_results[task_id] = None
                        self.background_exceptions[task_id] = sys.exc_info()
                        self._stop_requested = True
                        return

            print(f"[{task_id}] All API keys failed.")
            self.background_results[task_id] = None
            self.background_exceptions[task_id] = (Exception("All API keys failed"), None, None)
            self._stop_requested = True

        thread = threading.Thread(target=background_task, name=f"analysis_{task_id}")
        thread.daemon = True
        thread.start()
        self.background_threads.append(thread)
        return thread

    
    def check_background_exceptions(self):
        """Check if any background tasks have failed and raise their exceptions"""
        for task_id, exc_info in self.background_exceptions.items():
            if exc_info is not None:
                print(f"Re-raising exception from background task {task_id}")
                # Re-raise the exception in the main thread
                raise exc_info[1].with_traceback(exc_info[2])
    
    def wait_for_background_task(self, task_id, timeout=30):
        """Wait for specific background task to complete and check for exceptions"""
        start_time = time.time()
        while task_id not in self.background_results:
            if time.time() - start_time > timeout:
                print(f"Background task {task_id} timed out")
                return None
            
            # Check if we should stop due to background exceptions
            if self._stop_requested:
                self.check_background_exceptions()
                
            time.sleep(0.1)
        
        # Check for exceptions after task completion
        if task_id in self.background_exceptions and self.background_exceptions[task_id] is not None:
            self.check_background_exceptions()
            
        return self.background_results[task_id]
    
    def initial_clicks(self):
        """Execute initial clicks at the start of each iteration"""
        if self._stop_requested:
            self.check_background_exceptions()
        print("--- Initial Setup Clicks ---")
        self.click_at(900, 865)
        self.click_at(670, 590)
    
    def reload_page(self):
        """Reload current page and wait"""
        if self._stop_requested:
            self.check_background_exceptions()
        print("Reloading page...")
        self.hotkey_press('ctrl', 'r')
        self.wait(self.reload_delay)
    
    def switch_tab(self, tab_number):
        """Switch to specified tab"""
        self.hotkey_press('ctrl', str(tab_number))
    
    def window_snap(self, direction):
        """Snap window to left or right"""
        self.hotkey_press('ctrl', 'win', direction)
    
    def copy_paste_workflow(self, paste_coords, additional_clicks=None):
        """Complete copy-paste workflow"""
        if self._stop_requested:
            self.check_background_exceptions()
            
        pyautogui.scroll(-500)
        self.click_at(545, 825)
        
        self.click_at(*paste_coords)
        self.hotkey_press('ctrl', 'a')
        self.hotkey_press('ctrl', 'v')
        
        if additional_clicks:
            for coords in additional_clicks:
                self.click_at(*coords)

    
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

    
    def monitor_pixel_and_act(self):
        """Monitor a pixel and trigger automation if green is detected."""
        print("👀 Monitoring pixel for green color...")
        

        for i in range(0,1000):
            # Take a screenshot
            screenshot = pyautogui.screenshot()

            # Save the screenshot
            # self.save_screenshot(screenshot)

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
                time.sleep(self.check_interval) 
                # self.reload_page()
    
    def main_automation_sequence(self):
        """Execute the main automation sequence"""
        if self._stop_requested:
            self.check_background_exceptions()
            
        print("--- Processing Main Actions ---")
        self.click_at(1322, 821, clicks=2)
        self.click_at(1085, 600)
        self.wait( self.action_delay)
        self.click_at(1000, 535)
        self.hotkey_press('ctrl', 'w')
    
    def run_iteration(self, iteration_num, total_iterations):
        """Run a single iteration of the automation"""
        print(f"\n=== ITERATION {iteration_num} of {total_iterations} ===")
        
        # Check for background exceptions before starting iteration
        if self._stop_requested:
            self.check_background_exceptions()
        
        print("Starting automation...")
        self.wait(self.setup_delay)
        
        # Execute initial clicks
        for _ in range(4):
            pyautogui.scroll(-500)
            self.initial_clicks()
        
        # First sequence - Right side
        self.reload_page()
        pyautogui.scroll(-500)
        self.monitor_pixel_and_act()
        
        # Start background analysis for right side
        right_task_id = f"right_{iteration_num}"
        self.run_background_analysis(right_task_id)
        
        self.window_snap('right')
        for _ in range(4):
            pyautogui.scroll(-500)
            self.initial_clicks()
        
        # Second sequence - Left side  
        self.reload_page()
        pyautogui.scroll(-500)
        self.monitor_pixel_and_act()

        
        self.window_snap('left')
        
        # Copy-paste workflow - Right side
        additional_clicks = [(950, 625), (600, 697), (625, 927)]
        self.wait_for_background_task(right_task_id)  # This will check for exceptions
        self.copy_paste_workflow((545, 825), additional_clicks)
        # Start background analysis for left side
        left_task_id = f"left_{iteration_num}"
        self.run_background_analysis(left_task_id)
        self.window_snap('right')
                
        pyautogui.scroll(-500)
        # Copy-paste workflow - Left side
        self.wait_for_background_task(left_task_id)  # This will check for exceptions
        self.copy_paste_workflow((545, 825), additional_clicks)
        self.window_snap('left')
        
        print(f"Iteration {iteration_num} completed")
    
    def cleanup_threads(self):
        """Wait for all background threads to complete"""
        print("Waiting for all background threads to complete...")
        for thread in self.background_threads:
            if thread.is_alive():
                thread.join(timeout=8)


def main():
    """Main execution function"""
    NUM_ITERATIONS = 1000
    # NUM_ITERATIONS = 1
    
    bot = AutomationBot()
    
    print("=== AUTOMATION STARTING ===")
    print(f"Will run {NUM_ITERATIONS} iterations")
    print("Move mouse to top-left corner to emergency stop")
    
    try:
        for i in range(1, NUM_ITERATIONS + 1):
            bot.run_iteration(i, NUM_ITERATIONS)
            
        print("\n=== ALL ITERATIONS COMPLETED SUCCESSFULLY ===")
        
    except pyautogui.FailSafeException:
        print("\n=== EMERGENCY STOP ACTIVATED ===")
    except Exception as e:
        print(f"\n=== ERROR OCCURRED: {e} ===")
        import traceback
        traceback.print_exc()
    finally:
        bot.cleanup_threads()


if __name__ == "__main__":
    main()
