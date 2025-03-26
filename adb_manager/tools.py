# tools.py
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
from datetime import datetime
import platform
from PIL import Image, ImageTk  # For loading PNG icons
from .utils import execute_command, get_connected_devices, get_device_info, capture_screenshot, capture_screenrecord, stop_screenrecord, get_device_model_serial
import threading  # Import threading module

class ToolsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Configure the grid to expand and center the widgets
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)

        # Load PNG icons
        self.icons = {
            "tools": self.load_icon("tools.png", 24, 24),
            "device_info": self.load_icon("device_info.png", 24, 24),
            "volume_up": self.load_icon("volume_up.png", 24, 24),
            "volume_down": self.load_icon("volume_down.png", 24, 24),
            "power": self.load_icon("power.png", 24, 24),
            "camera": self.load_icon("camera.png", 24, 24),
            "reboot": self.load_icon("reboot.png", 24, 24),
            "scrcpy": self.load_icon("scrcpy.png", 24, 24),
            "screenshot": self.load_icon("screenshot.png", 24, 24),
            "screenrecord": self.load_icon("screenrecord.png", 24, 24),
            "stop_record": self.load_icon("stop_record.png", 24, 24),
            "folder": self.load_icon("folder.png", 24, 24),
            "restart": self.load_icon("restart.png", 24, 24),
            "recovery": self.load_icon("recovery.png", 24, 24),
            "bootloader": self.load_icon("bootloader.png", 24, 24),
        }

        # Device Info Section
        self.device_info_button = ttk.Button(self, text="Get Device Info", image=self.icons["device_info"], compound=tk.LEFT, command=self.show_device_info)
        self.device_info_button.grid(row=1, column=0, pady=5, sticky="ew")

        self.volume_up_button = ttk.Button(self, text="VOL+", image=self.icons["volume_up"], compound=tk.LEFT, command=self.volume_up)
        self.volume_up_button.grid(row=2, column=0, pady=5, sticky="ew")

        self.volume_down_button = ttk.Button(self, text="VOL-", image=self.icons["volume_down"], compound=tk.LEFT, command=self.volume_down)
        self.volume_down_button.grid(row=3, column=0, pady=5, sticky="ew")

        self.power_button = ttk.Button(self, text="Power", image=self.icons["power"], compound=tk.LEFT, command=self.power)
        self.power_button.grid(row=4, column=0, pady=5, sticky="ew")

        self.camera_button = ttk.Button(self, text="Camera", image=self.icons["camera"], compound=tk.LEFT, command=self.camera)
        self.camera_button.grid(row=5, column=0, pady=5, sticky="ew")

        self.reboot_button = ttk.Button(self, text="Reboot", image=self.icons["reboot"], compound=tk.LEFT, command=self.reboot)
        self.reboot_button.grid(row=6, column=0, pady=5, sticky="ew")

        self.scrcpy_button = ttk.Button(self, text="Execute Scrcpy", image=self.icons["scrcpy"], compound=tk.LEFT, command=self.execute_scrcpy)
        self.scrcpy_button.grid(row=7, column=0, pady=5, sticky="ew")

        # Screenshot and Screen Recording Section
        self.screenshot_button = ttk.Button(self, text="Take Screenshot", image=self.icons["screenshot"], compound=tk.LEFT, command=self.take_screenshot)
        self.screenshot_button.grid(row=1, column=2, pady=5, sticky="ew")

        self.start_screenrecord_button = ttk.Button(self, text="Start Screen Record", image=self.icons["screenrecord"], compound=tk.LEFT, command=self.start_screenrecord)
        self.start_screenrecord_button.grid(row=2, column=2, pady=5, sticky="ew")

        self.stop_screenrecord_button = ttk.Button(self, text="Stop Screen Record", image=self.icons["stop_record"], compound=tk.LEFT, command=self.stop_screenrecord, state=tk.DISABLED)
        self.stop_screenrecord_button.grid(row=3, column=2, pady=5, sticky="ew")

        self.open_folder_button = ttk.Button(self, text="Open Device Folder", image=self.icons["folder"], compound=tk.LEFT, command=self.open_pulled_device_folder)
        self.open_folder_button.grid(row=4, column=2, pady=5, sticky="ew")

        self.restart_adb_button = ttk.Button(self, text="Restart ADB Service", image=self.icons["restart"], compound=tk.LEFT, command=self.restart_adb)
        self.restart_adb_button.grid(row=5, column=2, pady=5, sticky="ew")

        self.reboot_recovery_button = ttk.Button(self, text="Reboot To Recovery", image=self.icons["recovery"], compound=tk.LEFT, command=self.reboot_recovery)
        self.reboot_recovery_button.grid(row=6, column=2, pady=5, sticky="ew")

        self.reboot_bootloader_button = ttk.Button(self, text="Reboot To Fastboot", image=self.icons["bootloader"], compound=tk.LEFT, command=self.reboot_bootloader)
        self.reboot_bootloader_button.grid(row=7, column=2, pady=5, sticky="ew")

        # Text widget for displaying device info
        self.text = tk.Text(self, height=15, width=30, font=("Arial", 10))
        self.text.grid(row=1, column=1, rowspan=7, padx=10, pady=5, sticky="nsew")

    def load_icon(self, icon_name, width, height):
        """Load and resize a PNG icon."""
        try:
            icon_path = os.path.join("icons", icon_name)  # Path to the icons folder
            icon = Image.open(icon_path)
            icon = icon.resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(icon)
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            return None

    def show_device_info(self):
        def run():
            device_serial = get_connected_devices()[0]
            device_info = get_device_info(device_serial)
            self.show_info_in_text_widget(device_info)

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def show_info_in_text_widget(self, device_info):
        self.text.delete("1.0", tk.END)
        for key, value in device_info.items():
            self.text.insert(tk.END, f"{key.replace('_', ' ').title()}: {value}\n")

    def volume_up(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} shell input keyevent KEYCODE_VOLUME_UP")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def volume_down(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} shell input keyevent KEYCODE_VOLUME_DOWN")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def power(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} shell input keyevent KEYCODE_POWER")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def camera(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} shell input keyevent KEYCODE_CAMERA")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def reboot(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} reboot")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def reboot_recovery(self):
        def run():
            device_serial = get_connected_devices()[0]
            try:
                execute_command(f"adb -s {device_serial} reboot recovery")
            except Exception as e:
                print("Error: No Device Connected.")
            else:
                messagebox.showinfo("Reboot Recovery", "Reboot to Recovery Mode started successfully!")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def reboot_bootloader(self):
        def run():
            device_serial = get_connected_devices()[0]
            try:
                execute_command(f"adb -s {device_serial} reboot bootloader")
            except Exception as e:
                print("Error: No Device Connected.")
            else:
                messagebox.showinfo("Reboot Bootloader", "Reboot to Bootloader Mode started successfully!")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def restart_adb(self):
        def run():
            device_serial = get_connected_devices()[0]
            execute_command(f"adb -s {device_serial} kill-server")
            execute_command(f"adb -s {device_serial} start-server")
            messagebox.showinfo("ADB Restart", "ADB Restart with successfully.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def execute_scrcpy(self):
        def run():
            choice = messagebox.askyesno("Record Video Stream", "Do you want to record video while mirroring?")
            # Determine scrcpy path based on OS
            if platform.system() == "Windows":
                scrcpy_path = r"./tools/scrcpy/scrcpy"
            elif platform.system() == "Linux":
                scrcpy_path = r"scrcpy"
            elif platform.system() == "Darwin":  # macOS support
                scrcpy_path = r"scrcpy"
            else:
                messagebox.showwarning("Scrcpy not found or not installed. Check if it's available.")
                return  # Exit function if scrcpy is not supported
            if choice:
                current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"Scrcpy_screenrecord-{current_time}.mp4"
                connected_devices = get_connected_devices()
                if connected_devices:
                    device_serial = connected_devices[0]
                    device_info = get_device_info(device_serial)
                    device_model = device_info.get('model')
                    if device_model:
                        directory_path = f"./device-pull/{device_model}-{device_serial}/screenrecord"
                        if not os.path.exists(directory_path):
                            os.makedirs(directory_path)
                        try:
                            subprocess.Popen([scrcpy_path, "--record", os.path.join(directory_path, filename)])
                            print("scrcpy with screen recording started successfully!")
                        except FileNotFoundError:
                            print("Error: scrcpy executable not found.")
                            messagebox.showerror("Error", "scrcpy executable not found.")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Error: Device model not found.")
                else:
                    print("Error: No connected devices.")
            else:
                try:
                    subprocess.Popen([scrcpy_path])
                    print("scrcpy started successfully!")
                except FileNotFoundError:
                    print("Error: scrcpy executable not found.")
                    messagebox.showerror("Error", "scrcpy executable not found.")
                except Exception as e:
                    print(f"Error: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def take_screenshot(self):
        def run():
            device_serial = get_connected_devices()[0]
            capture_screenshot(device_serial)
            messagebox.showinfo("Screenshot Captured", "Screenshot captured and saved successfully.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def start_screenrecord(self):
        def run():
            device_serial = get_connected_devices()[0]
            device_model, filename = capture_screenrecord(device_serial)
            if filename:
                self.current_filename = filename
                self.stop_screenrecord_button.config(state=tk.NORMAL)

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def stop_screenrecord(self):
        def run():
            device_serial = get_connected_devices()[0]
            device_model = get_device_info(device_serial)['model']
            if device_model:
                if self.current_filename:
                    stop_screenrecord(device_serial, device_model, self.current_filename)
                    self.current_filename = None
                self.stop_screenrecord_button.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("Device Model Not Found", "Device model information not found.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def open_pulled_device_folder(self):
        def run():
            device_serial = get_connected_devices()[0]
            device_model, device_serial = get_device_model_serial(device_serial)
            if device_model:
                # Sanitize the device model and serial for use in file paths
                sanitized_model = device_model.replace(":", "_").replace(".", "_")
                sanitized_serial = device_serial.replace(":", "_").replace(".", "_")
                
                # Construct the path to the pulled folder
                pulled_folder_path = os.path.join(os.getcwd(), "device-pull", f"{sanitized_model}-{sanitized_serial}")
                
                # Check if the directory exists
                if not os.path.exists(pulled_folder_path):
                    messagebox.showwarning("Directory Not Found", f"The directory '{pulled_folder_path}' does not exist.")
                    return
                
                # Open the folder using the appropriate command for the operating system
                if platform.system() == "Windows":
                    os.startfile(pulled_folder_path)  # Open folder in Windows Explorer
                elif platform.system() == "Linux" or platform.system() == "Darwin":
                    try:
                        if platform.system() == "Linux":
                            subprocess.Popen(["xdg-open", pulled_folder_path])  # Open folder in Linux file manager
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", pulled_folder_path])  # Open folder in macOS Finder
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to open folder: {e}")
                else:
                    messagebox.showwarning("Unsupported Platform", "Opening folders is not supported on this platform.")
            else:
                messagebox.showwarning("Device Model Not Found", "Device model information not found.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

