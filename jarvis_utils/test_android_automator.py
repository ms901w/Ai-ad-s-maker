import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
import os

# Adjust import path if your project structure is different or use PYTHONPATH
from android_automator import AndroidAutomator

class TestAndroidAutomator(unittest.TestCase):

    def setUp(self):
        # We patch _check_adb_device to prevent it from running actual ADB commands during setup of most tests
        # For specific tests of _check_adb_device, we'll unpatch or use a different approach.
        with patch.object(AndroidAutomator, '_check_adb_device', return_value=True) as _:
            self.automator = AndroidAutomator(adb_path="mock_adb")

    # Test for _check_adb_device (can be more involved if you want to simulate various outputs)
    @patch('subprocess.run')
    def test_check_adb_device_initialization(self, mock_run):
        # This test is for the _check_adb_device method itself
        # Mock ADB version call
        mock_version_result = MagicMock()
        mock_version_result.stdout = "Android Debug Bridge version x.y.z"
        mock_version_result.returncode = 0

        # Mock ADB devices call - simulate one device connected
        mock_devices_result = MagicMock()
        mock_devices_result.stdout = "List of devices attached\nemulator-5554\tdevice\n"
        mock_devices_result.returncode = 0

        mock_run.side_effect = [mock_version_result, mock_devices_result]

        # Instantiate without the setUp's patch for _check_adb_device
        automator_instance = AndroidAutomator(adb_path="mock_adb")
        self.assertTrue(automator_instance._check_adb_device()) # Directly test the outcome

        expected_calls = [
            call(['mock_adb', '--version'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW),
            call(['mock_adb', 'devices'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        ]
        mock_run.assert_has_calls(expected_calls)


    @patch('subprocess.run')
    def test_run_adb_command_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "Success output"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        success, output = self.automator._run_adb_command(["shell", "echo", "hello"])
        self.assertTrue(success)
        self.assertEqual(output, "Success output")
        mock_run.assert_called_once_with(
            ['mock_adb', 'shell', 'echo', 'hello'],
            capture_output=True, text=True, check=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW
        )

    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd", stderr="ADB Error"))
    def test_run_adb_command_called_process_error(self, mock_run):
        success, output = self.automator._run_adb_command(["shell", "error_command"])
        self.assertFalse(success)
        self.assertIn("ADB Command Error", output)
        self.assertIn("ADB Error", output)

    @patch('subprocess.run', side_effect=FileNotFoundError("adb not found"))
    def test_run_adb_command_file_not_found(self, mock_run):
        success, output = self.automator._run_adb_command(["devices"])
        self.assertFalse(success)
        self.assertEqual(output, "Error: ADB executable not found. Please ensure it's installed and in your PATH.")

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_list_connected_devices_success(self, mock_run_adb):
        mock_run_adb.return_value = (True, "List of devices attached\nemulator-5554\tdevice\nTA12345678\tdevice")
        success, devices = self.automator.list_connected_devices()
        self.assertTrue(success)
        self.assertEqual(devices, ["emulator-5554", "TA12345678"])
        mock_run_adb.assert_called_once_with(["devices"])

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_list_connected_devices_failure(self, mock_run_adb):
        mock_run_adb.return_value = (False, "ADB connection error")
        success, error_msg = self.automator.list_connected_devices()
        self.assertFalse(success)
        self.assertEqual(error_msg, "ADB connection error")

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_open_app_success(self, mock_run_adb):
        package_name = "com.example.app"
        # Simulate successful monkey command output
        mock_run_adb.return_value = (True, "Events injected: 1")

        success, message = self.automator.open_app(package_name)
        self.assertTrue(success)
        self.assertEqual(message, f"Attempting to open app '{package_name}'.")
        mock_run_adb.assert_called_once_with([
            "shell", "monkey", "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1"
        ], device_id=None)

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_open_app_failure_monkey(self, mock_run_adb):
        package_name = "com.example.fail"
        # Simulate monkey failing but app exists (hypothetically)
        mock_run_adb.side_effect = [
            (True, "monkey: error targeting package com.example.fail (reason: ...)."), # Monkey fails
            (True, f"package:{package_name}") # pm list packages shows it exists
        ]
        success, message = self.automator.open_app(package_name)
        self.assertFalse(success)
        self.assertIn(f"App '{package_name}' found, but could not be launched via monkey.", message)
        expected_calls = [
            call(['shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'], device_id=None),
            call(['shell', 'pm', 'list', 'packages', package_name], device_id=None)
        ]
        mock_run_adb.assert_has_calls(expected_calls)


    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_simulate_input_tap_success(self, mock_run_adb):
        mock_run_adb.return_value = (True, "") # Tap usually returns empty stdout on success
        success, message = self.automator.simulate_input_tap(100, 200)
        self.assertTrue(success)
        self.assertEqual(message, "")
        mock_run_adb.assert_called_once_with(["shell", "input", "tap", "100", "200"], device_id=None)

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_simulate_input_text_success(self, mock_run_adb):
        mock_run_adb.return_value = (True, "")
        text_to_type = "Hello Android"
        escaped_text = text_to_type.replace("'", "'\\''")
        success, message = self.automator.simulate_input_text(text_to_type)
        self.assertTrue(success)
        self.assertEqual(message, "")
        mock_run_adb.assert_called_once_with(["shell", "input", "text", escaped_text], device_id=None)

    @patch.object(AndroidAutomator, '_run_adb_command')
    @patch('os.path.dirname', return_value="local_screenshots") # Mock dirname to avoid issues with empty paths
    @patch('os.path.exists', return_value=False) # Mock path.exists to simulate dir not existing
    @patch('os.makedirs') # Mock makedirs
    def test_take_screenshot_android_success(self, mock_makedirs, mock_exists, mock_dirname, mock_run_adb):
        local_path = "local_screenshots/test_ss.png"
        device_path = "/sdcard/screenshot.png"

        # Simulate responses for screencap, pull, and rm
        mock_run_adb.side_effect = [
            (True, ""),  # screencap success
            (True, "1 file pulled."), # pull success
            (True, "")   # rm success (optional check)
        ]

        success, message = self.automator.take_screenshot_android(local_save_path=local_path, device_sdcard_path=device_path)

        self.assertTrue(success)
        self.assertEqual(message, f"Screenshot saved to {local_path}")

        mock_dirname.assert_called_once_with(local_path)
        mock_exists.assert_called_once_with("local_screenshots")
        mock_makedirs.assert_called_once_with("local_screenshots", exist_ok=True)

        expected_adb_calls = [
            call(["shell", "screencap", device_path], device_id=None),
            call(["pull", device_path, local_path], device_id=None),
            call(["shell", "rm", device_path], device_id=None)
        ]
        mock_run_adb.assert_has_calls(expected_adb_calls)

    @patch.object(AndroidAutomator, '_run_adb_command')
    def test_take_screenshot_android_screencap_fails(self, mock_run_adb):
        mock_run_adb.return_value = (False, "screencap error") # screencap fails

        success, message = self.automator.take_screenshot_android()
        self.assertFalse(success)
        self.assertIn("Failed to take screenshot on device", message)

    @patch.object(AndroidAutomator, '_run_adb_command')
    @patch('os.path.exists', return_value=True) # Assume local dir exists
    def test_take_screenshot_android_pull_fails(self, mock_exists, mock_run_adb):
        mock_run_adb.side_effect = [
            (True, ""), # screencap success
            (False, "pull error") # pull fails
        ]
        success, message = self.automator.take_screenshot_android()
        self.assertFalse(success)
        self.assertIn("Failed to pull screenshot from device", message)

if __name__ == '__main__':
    unittest.main()
