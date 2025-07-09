import subprocess
import os
import shutil
import sys # Added for platform check

# For more advanced control like volume, specific libraries might be needed in the future,
# e.g., pycaw for audio control, or platform-specific commands.

class WindowsAutomator:
    def __init__(self):
        # Potential future initialization for specific paths or settings
        pass

    def open_application(self, app_name):
        """
        Opens an application by its name.
        'app_name' can be the executable name (e.g., "notepad.exe")
        or a name that can be found via the system's PATH or 'start' command.
        Returns True if successful (or command sent), False otherwise.
        """
        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            # Using 'start' allows opening non-exe files with their default app
            # and also helps with apps found in PATH without needing full path.
            # Popen is used here for a non-blocking call.
            # Note: Error checking for Popen with shell=True can be tricky.
            # If 'start app_name' fails silently in the shell, Popen might not raise an exception.
            # We assume if Popen doesn't immediately error, the command was dispatched.
            subprocess.Popen(f'start {app_name}', shell=True, creationflags=creation_flags)
            return True, f"Attempting to open '{app_name}'."
        except Exception as e:
            # Log the exception for debugging purposes if you have a logging mechanism
            # print(f"DEBUG: Exception in open_application: {e}")
            return False, f"Error opening application '{app_name}': {e}"

    def list_directory_contents(self, dir_path="."):
        """
        Lists contents of a specified directory.
        Defaults to the current directory.
        Returns a tuple: (success_boolean, list_of_contents_or_error_message)
        """
        try:
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                return False, f"Error: Directory '{dir_path}' not found or is not a directory."
            contents = os.listdir(dir_path)
            return True, contents
        except Exception as e:
            return False, f"Error listing directory '{dir_path}': {e}"

    def system_command(self, command_key, confirmation_required=True):
        """
        Executes predefined system commands like shutdown or restart.
        Requires confirmation for dangerous commands.
        Returns True if command executed, False otherwise, along with a message.
        """
        commands = {
            "shutdown": "shutdown /s /t 1", # Shuts down in 1 second
            "restart": "shutdown /r /t 1",  # Restarts in 1 second
        }

        if command_key not in commands:
            return False, f"Unknown system command: {command_key}"

        if confirmation_required:
            # This would typically be handled by UI or calling logic.
            # For now, we assume confirmation is handled before this direct call if needed.
            pass

        try:
            # For safety during development, actual execution of shutdown/restart is commented out.
            # To enable, uncomment the subprocess.Popen line.
            # subprocess.Popen(commands[command_key], shell=True)
            return True, f"Simulating execution of system command: '{command_key}'. Actual command: '{commands[command_key]}'"
        except Exception as e:
            return False, f"Error executing system command '{command_key}': {e}"

    def take_screenshot(self, output_filepath="screenshot.png"):
        """
        Takes a screenshot. This is a placeholder.
        A robust implementation would use a library like Pillow (PIL) for screen capture
        or OS-specific tools.
        """
        # Example using Pillow (PIL) - uncomment and install Pillow if you want to try this
        # from PIL import ImageGrab
        # try:
        #     img = ImageGrab.grab()
        #     img.save(output_filepath)
        #     return True, f"Screenshot saved to {output_filepath}"
        # except Exception as e:
        #     # Ensure Pillow is installed: pip install Pillow
        #     return False, f"Error taking screenshot: {e}. (Ensure Pillow is installed if using ImageGrab)"
        return False, "Screenshot functionality is a placeholder and not yet implemented."


# Example Usage (for testing purposes)
if __name__ == '__main__':
    automator = WindowsAutomator()

    # Test opening an application
    # print("Testing application opening...")
    # success, message = automator.open_application("notepad.exe")
    # print(f"Open Notepad: {success}, {message}")

    # success, message = automator.open_application("chrome")
    # print(f"Open Chrome (if in PATH): {success}, {message}")

    # success, message = automator.open_application("non_existent_app_123xyz.exe")
    # print(f"Open NonExistentApp: {success}, {message}")


    # Test listing directory contents
    # print("\nTesting directory listing...")
    # success, result = automator.list_directory_contents("C:\\Windows" if sys.platform == "win32" else ".")
    # if success:
    #     print(f"Contents of {'C:\\Windows' if sys.platform == 'win32' else '.'} (first 10): {result[:10]}")
    # else:
    #     print(f"Error listing directory: {result}")

    # success, result = automator.list_directory_contents("C:\\NonExistentDir_123xyz")
    # print(f"Contents of NonExistentDir: {success}, {result}")

    # Test system commands (simulated)
    # print("\nTesting system commands (simulated)...")
    # success, message = automator.system_command("shutdown", confirmation_required=False)
    # print(f"Shutdown command: {success}, {message}")
    # success, message = automator.system_command("restart", confirmation_required=False)
    # print(f"Restart command: {success}, {message}")

    # Test screenshot (placeholder)
    # print("\nTesting screenshot (placeholder)...")
    # success, message = automator.take_screenshot("test_screenshot.png")
    # print(f"Screenshot: {success}, {message}")
    pass
