# adb_manager/__init__.py
from .utils import execute_command, get_connected_devices, get_device_info, capture_screenshot, capture_screenrecord, stop_screenrecord, get_device_model_serial
from .file_manager import FileManagerPage
from .apk_manager import APKManagerPage
from .network_manager import NetworkManagerPage
from .tools import ToolsPage
from .terminal import TerminalPage