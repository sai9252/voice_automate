import pyautogui
import time
import threading
import sys
from ai import analyse_audio_transcript_copy


class AutomationBot:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.setup_delay = 1
        self.action_delay = 0.3
        self.reload_wait = 4
        self.background_results = {}
        self.background_exceptions = {}  # Store exceptions from background tasks
        self.background_threads = []
        self._stop_requested = False  # Flag to stop iterations
        
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
        """Run audio analysis in background thread with exception handling"""
        def background_task():
            print(f"Starting background analysis {task_id}...")
            try:
                result = analyse_audio_transcript_copy()
                self.background_results[task_id] = result
                self.background_exceptions[task_id] = None  # No exception
                print(f"Background analysis {task_id} completed")
            except Exception as e:
                print(f"Background analysis {task_id} failed: {e}")
                # Store the full exception info for later re-raising
                self.background_exceptions[task_id] = sys.exc_info()
                self.background_results[task_id] = None
                self._stop_requested = True  # Signal main thread to stop
        
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
        self.click_at(800, 950)
        self.click_at(605, 690)
    
    def reload_page(self):
        """Reload current page and wait"""
        if self._stop_requested:
            self.check_background_exceptions()
        print("Reloading page...")
        self.hotkey_press('ctrl', 'r')
        self.wait(self.reload_wait)
    
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
        self.click_at(529, 900)
        
        self.click_at(*paste_coords)
        self.hotkey_press('ctrl', 'a')
        self.hotkey_press('ctrl', 'v')
        
        if additional_clicks:
            for coords in additional_clicks:
                self.click_at(*coords)
    
    def main_automation_sequence(self):
        """Execute the main automation sequence"""
        if self._stop_requested:
            self.check_background_exceptions()
            
        print("--- Processing Main Actions ---")
        self.click_at(1250, 383, clicks=2)
        self.click_at(1118, 680)
        self.click_at(1015, 617)
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
        self.main_automation_sequence()
        
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
        self.main_automation_sequence()

        # Start background analysis for left side
        left_task_id = f"left_{iteration_num}"
        self.run_background_analysis(left_task_id)
        
        self.window_snap('left')
        
        # Copy-paste workflow - Right side
        additional_clicks = [(857, 649), (574, 742), (590, 1020)]
        self.wait_for_background_task(right_task_id)  # This will check for exceptions
        self.copy_paste_workflow((575, 950), additional_clicks)
        self.window_snap('right')
                
        pyautogui.scroll(-500)
        # Copy-paste workflow - Left side
        self.wait_for_background_task(left_task_id)  # This will check for exceptions
        self.copy_paste_workflow((575, 950), additional_clicks)
        self.window_snap('left')
        
        print(f"Iteration {iteration_num} completed")
    
    def cleanup_threads(self):
        """Wait for all background threads to complete"""
        print("Waiting for all background threads to complete...")
        for thread in self.background_threads:
            if thread.is_alive():
                thread.join(timeout=10)


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
