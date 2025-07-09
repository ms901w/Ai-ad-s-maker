import subprocess
import os

class AndroidAutomator:
    def __init__(self, adb_path="adb"):
        """
        Initializes the AndroidAutomator.
        :param adb_path: Path to the ADB executable. Defaults to "adb", assuming it's in PATH.
        """
        self.adb_path = adb_path
        self._check_adb_device()

    def _check_adb_device(self):
        """
        Checks if ADB is installed and if any device/emulator is connected.
        Logs messages but doesn't prevent instantiation. Calls to methods will fail if no device.
        """
        try:
            subprocess.run([self.adb_path, "--version"], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: ADB command not found or not working. Please ensure ADB is installed and in your PATH.")
            # In a real UI app, this would be logged or shown as a status.
            return False

        try:
            result = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            devices = result.stdout.strip().split('\n')[1:] # Skip header line
            if not devices or (len(devices) == 1 and not devices[0].strip()):
                print("Warning: No Android devices or emulators found connected via ADB.")
                return False

            # Check if any device is actually listed (not just empty lines or "offline")
            active_devices = [line for line in devices if line.strip() and not line.endswith('\toffline')]
            if not active_devices:
                print("Warning: No active Android devices or emulators found. Some might be offline.")
                return False
            print(f"ADB initialized. Connected devices/emulators found: {active_devices}")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error checking ADB devices: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while checking ADB devices: {e}")
            return False


    def _run_adb_command(self, command_parts, device_id=None):
        """
        Helper function to run an ADB command.
        :param command_parts: A list of command arguments for ADB (e.g., ["shell", "input", "text", "hello"]).
        :param device_id: Optional specific device ID to target.
        :return: Tuple (success_boolean, output_string_or_error_message)
        """
        base_command = [self.adb_path]
        if device_id:
            base_command.extend(["-s", device_id])

        full_command = base_command + command_parts

        try:
            # print(f"Executing ADB command: {' '.join(full_command)}") # For debugging
            result = subprocess.run(full_command, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            return True, result.stdout.strip()
        except FileNotFoundError:
            return False, "Error: ADB executable not found. Please ensure it's installed and in your PATH."
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip() if e.stderr else e.stdout.strip()
            return False, f"ADB Command Error: '{' '.join(full_command)}' failed with: {error_message}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def list_connected_devices(self):
        """
        Lists all connected Android devices and emulators.
        :return: Tuple (success_boolean, list_of_devices_or_error_message)
        """
        success, output = self._run_adb_command(["devices"])
        if success:
            lines = output.strip().split('\n')
            # First line is "List of devices attached", so skip it.
            # Each device line is like "emulator-5554\tdevice"
            devices = [line.split('\t')[0] for line in lines[1:] if line.strip()]
            return True, devices
        return False, output # Output contains the error message

    def open_app(self, package_name, device_id=None):
        """
        Opens an application using its package name.
        To find package name: `adb shell pm list packages` and then `adb shell monkey -p your.package.name -c android.intent.category.LAUNCHER 1`
        Often, the main activity launches by default with `am start -n package_name/activity_name`
        A simpler way that often works is `monkey`.
        :param package_name: The package name (e.g., "com.android.chrome").
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        # Using monkey is a common way to launch the main activity of a package
        success, output = self._run_adb_command([
            "shell", "monkey", "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1"
        ], device_id=device_id)

        if success:
            if "Events injected: 1" in output or output == "": # Some devices give no output on success for monkey
                return True, f"Attempting to open app '{package_name}'."
            else:
                # Check if package exists if monkey fails in a specific way
                exists_success, exists_output = self._run_adb_command(["shell", "pm", "list", "packages", package_name], device_id=device_id)
                if exists_success and package_name in exists_output:
                    return False, f"App '{package_name}' found, but could not be launched via monkey. Output: {output}"
                else:
                    return False, f"Failed to open app '{package_name}'. It might not be installed or launchable. ADB Output: {output}"
        return False, output


    def send_intent(self, intent_action, data_uri=None, package=None, component_name=None, device_id=None):
        """
        Sends a broadcast intent. More complex intents (start activity with result) are not covered here.
        Example: adb shell am broadcast -a com.example.MY_ACTION --es message "Hello"
        :param intent_action: The action string (e.g., "android.intent.action.VIEW").
        :param data_uri: Optional data URI for the intent.
        :param package: Optional package to restrict the intent to.
        :param component_name: Optional explicit component name (package/class).
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        command = ["shell", "am", "start"] # Using 'am start' as it's common for basic intents like VIEW
        if package:
            command.extend(["-p", package])
        if component_name:
            command.extend(["-n", component_name])
        command.extend(["-a", intent_action])
        if data_uri:
            command.extend(["-d", data_uri])

        success, output = self._run_adb_command(command, device_id=device_id)
        if success:
            # 'am start' output can vary. "Starting: Intent { ... }" is common.
            if "Error" not in output and "Exception" not in output: # Basic check
                return True, f"Intent '{intent_action}' sent. Output: {output}"
            else:
                return False, f"Error sending intent '{intent_action}'. Output: {output}"
        return False, output

    def simulate_input_tap(self, x, y, device_id=None):
        """
        Simulates a tap at the given X, Y coordinates.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        return self._run_adb_command(["shell", "input", "tap", str(x), str(y)], device_id=device_id)

    def simulate_input_swipe(self, x1, y1, x2, y2, duration_ms=300, device_id=None):
        """
        Simulates a swipe from (x1,y1) to (x2,y2) over a duration.
        :param x1, y1: Start coordinates.
        :param x2, y2: End coordinates.
        :param duration_ms: Duration of the swipe in milliseconds.
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        return self._run_adb_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration_ms)
        ], device_id=device_id)

    def simulate_input_text(self, text_to_type, device_id=None):
        """
        Simulates typing text. Note: This types text where the current focus is.
        Special characters might need escaping or alternative methods.
        :param text_to_type: The string to type.
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        # ADB 'input text' handles spaces correctly if the string is quoted by the shell.
        # subprocess handles argument quoting, so we pass the text as one argument.
        # However, special characters like ' " ` $ \ ! might still be problematic.
        # For more complex text, one might need to escape it or use alternative adb input methods.
        escaped_text = text_to_type.replace("'", "'\\''") # Basic escaping for single quotes for shell
        return self._run_adb_command(["shell", "input", "text", escaped_text], device_id=device_id)

    def take_screenshot_android(self, local_save_path="android_screenshot.png", device_sdcard_path="/sdcard/screenshot.png", device_id=None):
        """
        Takes a screenshot on the Android device and pulls it to the local machine.
        :param local_save_path: Path to save the screenshot locally.
        :param device_sdcard_path: Temporary path to store screenshot on device.
        :param device_id: Optional specific device ID.
        :return: Tuple (success_boolean, message)
        """
        # 1. Take screenshot on device
        success, output = self._run_adb_command(["shell", "screencap", device_sdcard_path], device_id=device_id)
        if not success:
            return False, f"Failed to take screenshot on device: {output}"

        # 2. Pull screenshot from device
        # Ensure local directory exists
        local_dir = os.path.dirname(local_save_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        success_pull, output_pull = self._run_adb_command(["pull", device_sdcard_path, local_save_path], device_id=device_id)
        if not success_pull:
            return False, f"Failed to pull screenshot from device ({device_sdcard_path}) to {local_save_path}: {output_pull}"

        # 3. (Optional) Remove screenshot from device
        self._run_adb_command(["shell", "rm", device_sdcard_path], device_id=device_id)
        # We don't strictly check success of rm, as the main goal is achieved.

        return True, f"Screenshot saved to {local_save_path}"

# Example Usage (for testing purposes - requires connected Android device/emulator with ADB enabled)
if __name__ == '__main__':
    automator = AndroidAutomator() # Assumes adb is in PATH

    print("\n--- Checking Devices ---")
    devices_success, devices_list = automator.list_connected_devices()
    if devices_success:
        print("Connected devices/emulators:", devices_list)
        if not devices_list:
            print("No devices found. Please connect a device or start an emulator with ADB enabled.")
            exit()

        # Pick the first device for further tests if available
        target_device = devices_list[0] if devices_list else None
        print(f"Using device: {target_device} for subsequent tests if applicable.")

        if target_device:
            print("\n--- Testing App Launch (Chrome) ---")
            # You might need to change "com.android.chrome" if Chrome is not installed or has a different package name on your test device/emulator
            app_pkg = "com.android.chrome"
            # To find chrome: adb shell pm list packages | grep chrome
            # On emulators, it's often com.android.chrome
            success, msg = automator.open_app(app_pkg, device_id=target_device)
            print(f"Open app '{app_pkg}': {success}, Message: {msg}")
            if not success:
                print(f"INFO: To test app opening, ensure '{app_pkg}' is installed on '{target_device}'.")


            # print("\n--- Testing Screenshot ---")
            # success, msg = automator.take_screenshot_android(local_save_path="test_android_ss.png", device_id=target_device)
            # print(f"Take screenshot: {success}, Message: {msg}")
            # if success:
            #     print(f"Screenshot saved to test_android_ss.png in the script's directory.")

            # print("\n--- Testing Input Tap (example coordinates, likely does nothing specific) ---")
            # success, msg = automator.simulate_input_tap(500, 1000, device_id=target_device) # Example coords
            # print(f"Simulate tap: {success}, Message: {msg}")

            # print("\n--- Testing Input Text (example, will type where focus is) ---")
            # success, msg = automator.simulate_input_text("Hello Android from Jarvis", device_id=target_device)
            # print(f"Simulate text input: {success}, Message: {msg}")
            # print("INFO: Text input occurs at the currently focused input field on the Android device.")

    else:
        print("Failed to list devices or ADB error:", devices_list)

    print("\nNote: For these tests to work, an Android device or emulator must be connected,")
    print("USB debugging must be enabled, and 'adb' must be in your system's PATH.")
    print("Some commands like 'open_app' require knowing the correct package name.")
