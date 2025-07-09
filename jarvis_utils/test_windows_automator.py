import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess
import sys # Added for platform check

# Adjust import path
from windows_automator import WindowsAutomator

class TestWindowsAutomator(unittest.TestCase):

    def setUp(self):
        self.automator = WindowsAutomator()

    @patch('subprocess.Popen')
    def test_open_application_success(self, mock_popen):
        """Test successfully opening an application."""
        app_name = "notepad.exe"

        # Mock Popen to avoid actual execution and ensure it doesn't raise an exception
        mock_process_instance = MagicMock()
        mock_popen.return_value = mock_process_instance

        success, message = self.automator.open_application(app_name)

        self.assertTrue(success, f"open_application failed unexpectedly. Message: {message}")
        self.assertEqual(message, f"Attempting to open '{app_name}'.")

        expected_creation_flags = 0
        if sys.platform == "win32":
            expected_creation_flags = subprocess.CREATE_NO_WINDOW

        mock_popen.assert_called_once_with(
            f'start {app_name}',
            shell=True,
            creationflags=expected_creation_flags
        )

    @patch('subprocess.Popen', side_effect=Exception("Test Popen Error"))
    def test_open_application_failure_popen_exception(self, mock_popen):
        """Test failing to open an application when Popen raises an exception."""
        app_name = "error_app.exe"
        success, message = self.automator.open_application(app_name)
        self.assertFalse(success)
        self.assertIn(f"Error opening application '{app_name}': Test Popen Error", message)

        expected_creation_flags = 0
        if sys.platform == "win32":
            expected_creation_flags = subprocess.CREATE_NO_WINDOW

        mock_popen.assert_called_once_with(
            f'start {app_name}',
            shell=True,
            creationflags=expected_creation_flags
        )

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=["file1.txt", "folderA"])
    def test_list_directory_contents_success(self, mock_listdir, mock_isdir, mock_exists):
        """Test successfully listing directory contents."""
        dir_path = "C:\\test_dir"
        success, contents = self.automator.list_directory_contents(dir_path)
        self.assertTrue(success)
        self.assertEqual(contents, ["file1.txt", "folderA"])
        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)
        mock_listdir.assert_called_once_with(dir_path)

    @patch('os.path.exists', return_value=False)
    def test_list_directory_contents_not_exists(self, mock_exists):
        """Test listing directory when path does not exist."""
        dir_path = "C:\\non_existent_dir"
        success, message = self.automator.list_directory_contents(dir_path)
        self.assertFalse(success)
        self.assertIn("not found or is not a directory", message)
        mock_exists.assert_called_once_with(dir_path)

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    def test_list_directory_contents_not_a_dir(self, mock_isdir, mock_exists):
        """Test listing directory when path is not a directory."""
        dir_path = "C:\\file_not_dir"
        success, message = self.automator.list_directory_contents(dir_path)
        self.assertFalse(success)
        self.assertIn("not found or is not a directory", message)
        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)

    @patch('os.listdir', side_effect=Exception("Permission Denied"))
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_list_directory_contents_exception(self, mock_isdir, mock_exists, mock_listdir):
        """Test listing directory contents with a generic exception."""
        dir_path = "C:\\protected_dir"
        success, message = self.automator.list_directory_contents(dir_path)
        self.assertFalse(success)
        self.assertIn(f"Error listing directory '{dir_path}': Permission Denied", message)

    def test_system_command_shutdown_simulation(self):
        """Test simulated shutdown command."""
        success, message = self.automator.system_command("shutdown", confirmation_required=False)
        self.assertTrue(success)
        self.assertIn("Simulating execution of system command: 'shutdown'", message)

    def test_system_command_restart_simulation(self):
        """Test simulated restart command."""
        success, message = self.automator.system_command("restart", confirmation_required=False)
        self.assertTrue(success)
        self.assertIn("Simulating execution of system command: 'restart'", message)

    def test_system_command_unknown(self):
        """Test unknown system command."""
        success, message = self.automator.system_command("unknown_cmd")
        self.assertFalse(success)
        self.assertEqual(message, "Unknown system command: unknown_cmd")

    def test_take_screenshot_placeholder(self):
        """Test the placeholder screenshot functionality."""
        success, message = self.automator.take_screenshot("test_ss.png")
        self.assertFalse(success)
        self.assertEqual(message, "Screenshot functionality is a placeholder and not yet implemented.")

if __name__ == '__main__':
    unittest.main()
