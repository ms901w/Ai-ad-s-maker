import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QTextEdit
from PyQt5.QtCore import Qt, QTimer
import datetime

class JarvisLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # self.windows_automator = None # Will be loaded on first command

    def init_ui(self):
        self.setWindowTitle('Jarvis AI Launcher')
        self.setGeometry(100, 100, 600, 400) # x, y, width, height

        # Layout
        layout = QVBoxLayout()

        # Clock Label
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignRight)
        self.clock_label.setStyleSheet("font-size: 16px; color: #A0A0A0;")
        layout.addWidget(self.clock_label)

        # "Welcome" or Status Label (placeholder)
        self.status_label = QLabel("Welcome to Jarvis")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.status_label)

        # Command Input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 5px;")
        self.command_input.returnPressed.connect(self.handle_command)
        layout.addWidget(self.command_input)

        # Output/Log Area (placeholder)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("font-size: 14px; background-color: #F0F0F0; border-radius: 5px;")
        self.output_area.setText("Command history or responses will appear here.")
        layout.addWidget(self.output_area)

        # Set main layout
        self.setLayout(layout)

        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000) # Update every second
        self.update_clock() # Initial call

        self.show()

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def handle_command(self):
        command_text = self.command_input.text()
        if command_text:
            # This will call the new command processing method
            self.process_ui_command(command_text)
            self.command_input.clear()

    def process_ui_command(self, command_text):
        """
        Processes commands entered through the UI.
        This will eventually interact with the Core Orchestrator.
        For Phase 1, it might directly call automator methods or use a simple dispatcher.
        """
        self.log_message(f"User command: {command_text}")

        # Simple command parsing for Phase 1
        parts = command_text.lower().split()
        if not parts:
            return

        action = parts[0]

        # Load Windows Automator if not already loaded and action implies Windows
        # More sophisticated routing will be part of the Core Orchestrator later
        if action in ["list", "system"] or ("open" in action and "android" not in command_text.lower()):
            if not hasattr(self, 'windows_automator_instance') or self.windows_automator_instance is None:
                self.load_windows_automator()

        # Load Android Automator if an Android-related command is detected
        if "android" in command_text.lower() or action == "adb":
            if not hasattr(self, 'android_automator_instance') or self.android_automator_instance is None:
                self.load_android_automator()

        # Command Handling
        if action == "hello":
            self.log_message("Jarvis: Hello there!")
        elif action == "open" and len(parts) > 1:
            self.handle_open_command(parts, command_text)
        elif action == "list" and len(parts) > 1:
            self.handle_list_command(parts)
        elif action == "system" and len(parts) > 1:
            self.handle_system_command(parts)
        elif action == "screenshot":
            self.handle_screenshot_command(parts)
        elif action == "adb" and len(parts) > 1:
            self.handle_adb_command(parts)
        else:
            self.log_message(f"Jarvis: Command '{command_text}' not recognized or arguments missing.")

    def load_windows_automator(self):
        if not hasattr(self, 'windows_automator_instance') or self.windows_automator_instance is None:
            try:
                from jarvis_utils.windows_automator import WindowsAutomator
                self.windows_automator_instance = WindowsAutomator()
                self.log_message("Jarvis: WindowsAutomator loaded.")
            except ImportError:
                self.log_message("Jarvis Error: Could not import WindowsAutomator module.")
                self.windows_automator_instance = None
            except Exception as e:
                self.log_message(f"Jarvis Error: Failed to initialize WindowsAutomator: {e}")
                self.windows_automator_instance = None
        return self.windows_automator_instance

    def load_android_automator(self):
        if not hasattr(self, 'android_automator_instance') or self.android_automator_instance is None:
            try:
                from jarvis_utils.android_automator import AndroidAutomator
                self.android_automator_instance = AndroidAutomator()
                self.log_message("Jarvis: AndroidAutomator loaded. Initializing ADB connection...")
                # AndroidAutomator __init__ now includes a basic check.
                # We can add more detailed feedback if needed.
                # success, devices = self.android_automator_instance.list_connected_devices()
                # if success and devices:
                #    self.log_message(f"Jarvis (Droid): Connected devices: {devices}")
                # elif success: # No devices but command was successful
                #    self.log_message("Jarvis (Droid): ADB command successful, but no devices found/listed.")
                # else: # Error
                #    self.log_message(f"Jarvis (Droid): Error checking ADB devices: {devices}")

            except ImportError:
                self.log_message("Jarvis Error: Could not import AndroidAutomator module.")
                self.android_automator_instance = None
            except Exception as e:
                self.log_message(f"Jarvis Error: Failed to initialize AndroidAutomator: {e}")
                self.android_automator_instance = None
        return self.android_automator_instance

    def handle_open_command(self, parts, command_text):
        # Default to Windows if "on android" is not specified
        target_os = "windows"
        app_name_parts = parts[1:] # e.g., ["chrome"] or ["com.example.app"]

        # Check for "on android" or "on windows"
        # Command: "open <app_name> on <os_target>"
        if "on" in app_name_parts:
            try:
                on_index = app_name_parts.index("on")
                # Ensure there's something after "on"
                if on_index + 1 < len(app_name_parts):
                    specified_os = app_name_parts[on_index+1].lower()
                    if specified_os in ["android", "windows"]:
                        target_os = specified_os
                        app_name_parts = app_name_parts[:on_index] # Get parts before "on"
                    # If not "android" or "windows", it might be part of the app name
                # If "on" is the last word, it's part of the app name
            except ValueError: # "on" not found
                pass # app_name_parts remains as is

        app_name = " ".join(app_name_parts)
        if not app_name:
            self.log_message("Jarvis: No application name specified for 'open' command.")
            return

        if target_os == "windows":
            win_automator = self.load_windows_automator()
            if win_automator:
                success, message = win_automator.open_application(app_name)
                self.log_message(f"Jarvis (Win): {message}")
            else:
                self.log_message("Jarvis: WindowsAutomator not available/loaded.")
        elif target_os == "android":
            droid_automator = self.load_android_automator()
            if droid_automator:
                self.log_message(f"Jarvis (Droid): Attempting to open '{app_name}'. (Note: This should be a package name for Android).")
                success, message = droid_automator.open_app(app_name) # app_name should be package name
                self.log_message(f"Jarvis (Droid): {message}")
            else:
                self.log_message("Jarvis: AndroidAutomator not available/loaded, or no device connected.")
        else: # Should not happen if logic above is correct
            self.log_message(f"Jarvis: Target OS '{target_os}' not recognized for open command.")

    def handle_list_command(self, parts): # Assuming "list" is for Windows for now
        # Future: "list /path on windows" or "list /sdcard/ on android"
        dir_path = " ".join(parts[1:])
        win_automator = self.load_windows_automator() # Default to Windows
        if win_automator:
            success, result = win_automator.list_directory_contents(dir_path)
            if success:
                self.log_message(f"Jarvis (Win): Contents of '{dir_path}':")
                if isinstance(result, list):
                    for item in result:
                        self.log_message(f"  - {item}")
                else:
                    self.log_message(f"  {result}") # Should be error message
            else:
                self.log_message(f"Jarvis (Win): {result}")
        else:
            self.log_message("Jarvis: WindowsAutomator not available/loaded.")

    def handle_system_command(self, parts): # Assuming "system" is for Windows
        command_key = parts[1]
        win_automator = self.load_windows_automator()
        if win_automator:
            success, message = win_automator.system_command(command_key, confirmation_required=False)
            self.log_message(f"Jarvis (Win): {message}")
        else:
            self.log_message("Jarvis: WindowsAutomator not available/loaded.")

    def handle_screenshot_command(self, parts):
        target_os = "windows" # Default
        filename_base = "jarvis_screenshot"

        # "screenshot android" or "screenshot windows" or just "screenshot"
        # "screenshot android my_capture.png"
        # "screenshot my_desktop.png" (implies windows)
        custom_filename = None

        arg1 = parts[1].lower() if len(parts) > 1 else None
        arg2 = parts[2] if len(parts) > 2 else None

        if arg1 == "android":
            target_os = "android"
            if arg2: custom_filename = arg2
        elif arg1 == "windows":
            target_os = "windows"
            if arg2: custom_filename = arg2
        elif arg1 and not arg1 in ["android", "windows"]: # e.g. "screenshot mypic.png"
            custom_filename = arg1 # Assumes it's a filename for the default OS (Windows)

        # Ensure filename has an extension
        if custom_filename and not custom_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            custom_filename += ".png"

        final_filename = custom_filename if custom_filename else f"{filename_base}_{target_os}.png"

        if target_os == "windows":
            win_automator = self.load_windows_automator()
            if win_automator:
                success, message = win_automator.take_screenshot(final_filename)
                self.log_message(f"Jarvis (Win): {message}")
            else:
                self.log_message("Jarvis: WindowsAutomator not available/loaded.")
        elif target_os == "android":
            droid_automator = self.load_android_automator()
            if droid_automator:
                success, message = droid_automator.take_screenshot_android(final_filename)
                self.log_message(f"Jarvis (Droid): {message}")
            else:
                self.log_message("Jarvis: AndroidAutomator not available/loaded, or no device connected.")
        else: # Should not happen
            self.log_message(f"Jarvis: Target OS '{target_os}' not recognized for screenshot.")


    def handle_adb_command(self, parts):
        droid_automator = self.load_android_automator()
        if not droid_automator:
            self.log_message("Jarvis: AndroidAutomator not available/loaded, or no device connected.")
            return

        sub_command = parts[1] # e.g., "devices", "tap", "text", "swipe"
        args = parts[2:]       # Arguments for the sub_command

        # Note: AndroidAutomator's methods accept an optional 'device_id'.
        # Parsing a device ID (e.g., from "adb -s emulator-5554 tap 100 200") is not implemented here
        # for simplicity. It would require more sophisticated parsing in this handler.
        # Currently, commands will go to the default/first device ADB targets.

        if sub_command == "devices":
            success, dev_list = droid_automator.list_connected_devices()
            if success:
                if dev_list:
                    self.log_message(f"Jarvis (Droid) Connected Devices/Emulators:")
                    for dev in dev_list:
                        self.log_message(f"  - {dev}")
                else:
                    self.log_message("Jarvis (Droid): No devices found connected via ADB.")
            else:
                self.log_message(f"Jarvis (Droid) Error listing devices: {dev_list}")
        elif sub_command == "tap" and len(args) == 2:
            try:
                x, y = int(args[0]), int(args[1])
                success, msg = droid_automator.simulate_input_tap(x,y)
                self.log_message(f"Jarvis (Droid) Tap at ({x},{y}): {msg}")
            except ValueError:
                self.log_message("Jarvis (Droid) Error: Invalid coordinates for tap. Usage: adb tap <x> <y>")
        elif sub_command == "swipe" and len(args) >= 4 : # adb swipe x1 y1 x2 y2 [duration_ms]
            try:
                x1,y1,x2,y2 = map(int, args[0:4])
                duration = int(args[4]) if len(args) > 4 else 300 # Default duration
                success, msg = droid_automator.simulate_input_swipe(x1,y1,x2,y2,duration_ms=duration)
                self.log_message(f"Jarvis (Droid) Swipe from ({x1},{y1}) to ({x2},{y2}) duration {duration}ms: {msg}")
            except ValueError:
                self.log_message("Jarvis (Droid) Error: Invalid coordinates/duration for swipe. Usage: adb swipe <x1> <y1> <x2> <y2> [duration_ms]")
        elif sub_command == "text" and args:
            text_to_type = " ".join(args)
            success, msg = droid_automator.simulate_input_text(text_to_type)
            self.log_message(f"Jarvis (Droid) Text input '{text_to_type}': {msg}")
        else:
            self.log_message(f"Jarvis (Droid): Unknown ADB sub-command '{sub_command}' or incorrect arguments.")
            self.log_message("Supported ADB via UI: devices, tap <x> <y>, swipe <x1> <y1> <x2> <y2> [duration_ms], text <string to type>")


    def log_message(self, message):
        current_log = self.output_area.toPlainText()
        if current_log == "Command history or responses will appear here.":
            current_log = ""

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message_str = str(message) # Ensure message is a string
        self.output_area.setText(f"{current_log}{timestamp} - {message_str}\n")
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = JarvisLauncher()
    sys.exit(app.exec_())
