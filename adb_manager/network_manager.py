# network_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from PIL import Image, ImageTk  # For loading PNG icons
import os
import threading  # Import threading module

class NetworkManagerPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Configure the grid to expand and center the widgets
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Load PNG icons
        self.icons = {
            "network": self.load_icon("network.png", 24, 24),
            "wifi": self.load_icon("wifi.png", 24, 24),
            "bluetooth": self.load_icon("bluetooth.png", 24, 24),
            "airplane": self.load_icon("airplane.png", 24, 24),
            "data": self.load_icon("data.png", 24, 24),
            "connect": self.load_icon("connect.png", 24, 24),
            "disconnect": self.load_icon("disconnect.png", 24, 24),
            "ip": self.load_icon("ip.png", 24, 24),
            "network_manager": self.load_icon("network_manager.png", 24, 24),
        }

        # IP Address Section
        self.ip_entry = ttk.Entry(self, width=20)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.get_ip_button = ttk.Button(self, text="Get IP Address", image=self.icons["ip"], compound=tk.LEFT, command=self.get_ip_address)
        self.get_ip_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.connect_adb_button = ttk.Button(self, text="Connect", image=self.icons["connect"], compound=tk.LEFT, command=self.connect_adb)
        self.connect_adb_button.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.disconnect_adb_button = ttk.Button(self, text="Disconnect", image=self.icons["disconnect"], compound=tk.LEFT, command=self.disconnect_adb)
        self.disconnect_adb_button.grid(row=1, column=4, padx=5, pady=5, sticky="ew")

        # Network Controls Section
        self.wifi_icon = ttk.Label(self, text="Wi-Fi", image=self.icons["wifi"], compound=tk.LEFT, font=("Arial", 10))
        self.wifi_icon.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.enable_wifi_button = ttk.Button(self, text="Enable Wi-Fi", image=self.icons["wifi"], compound=tk.LEFT, command=self.enable_wifi)
        self.enable_wifi_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.disable_wifi_button = ttk.Button(self, text="Disable Wi-Fi", image=self.icons["wifi"], compound=tk.LEFT, command=self.disable_wifi)
        self.disable_wifi_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.bluetooth_icon = ttk.Label(self, text="Bluetooth", image=self.icons["bluetooth"], compound=tk.LEFT, font=("Arial", 10))
        self.bluetooth_icon.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

        self.enable_bt_button = ttk.Button(self, text="Enable Bluetooth", image=self.icons["bluetooth"], compound=tk.LEFT, command=self.enable_bluetooth)
        self.enable_bt_button.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        self.disable_bt_button = ttk.Button(self, text="Disable Bluetooth", image=self.icons["bluetooth"], compound=tk.LEFT, command=self.disable_bluetooth)
        self.disable_bt_button.grid(row=4, column=2, padx=5, pady=5, sticky="ew")

        self.airplane_icon = ttk.Label(self, text="Airplane Mode", image=self.icons["airplane"], compound=tk.LEFT, font=("Arial", 10))
        self.airplane_icon.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        self.enable_airplane_button = ttk.Button(self, text="Enable Airplane Mode", image=self.icons["airplane"], compound=tk.LEFT, command=self.enable_airplane)
        self.enable_airplane_button.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        self.disable_airplane_button = ttk.Button(self, text="Disable Airplane Mode", image=self.icons["airplane"], compound=tk.LEFT, command=self.disable_airplane)
        self.disable_airplane_button.grid(row=4, column=3, padx=5, pady=5, sticky="ew")

        self.data_icon = ttk.Label(self, text="Mobile Data", image=self.icons["data"], compound=tk.LEFT, font=("Arial", 10))
        self.data_icon.grid(row=2, column=4, padx=10, pady=5, sticky="ew")

        self.enable_data_button = ttk.Button(self, text="Enable Mobile Data", image=self.icons["data"], compound=tk.LEFT, command=self.enable_data)
        self.enable_data_button.grid(row=3, column=4, padx=5, pady=5, sticky="ew")

        self.disable_data_button = ttk.Button(self, text="Disable Mobile Data", image=self.icons["data"], compound=tk.LEFT, command=self.disable_data)
        self.disable_data_button.grid(row=4, column=4, padx=5, pady=5, sticky="ew")

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

    def enable_wifi(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "wifi", "enable"])
                messagebox.showinfo("Success", "Wi-Fi enabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error enabling Wi-Fi: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def disable_wifi(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "wifi", "disable"])
                messagebox.showinfo("Success", "Wi-Fi disabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error disabling Wi-Fi: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def enable_bluetooth(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "bluetooth", "enable"])
                messagebox.showinfo("Success", "Bluetooth enabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error enabling Bluetooth: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def disable_bluetooth(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "bluetooth", "disable"])
                messagebox.showinfo("Success", "Bluetooth disabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error disabling Bluetooth: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def enable_airplane(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "cmd", "connectivity", "airplane-mode", "enable"])
                messagebox.showinfo("Success", "Airplane Mode enabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error enabling Airplane Mode: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def disable_airplane(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "cmd", "connectivity", "airplane-mode", "disable"])
                messagebox.showinfo("Success", "Airplane Mode disabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error disabling Airplane Mode: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def enable_data(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "data", "enable"])
                messagebox.showinfo("Success", "Mobile Data enabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error enabling Mobile Data: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def disable_data(self):
        def run():
            try:
                subprocess.check_output(["adb", "shell", "svc", "data", "disable"])
                messagebox.showinfo("Success", "Mobile Data disabled successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error disabling Mobile Data: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def connect_adb(self):
        def run():
            ip_address = self.ip_entry.get()
            if not ip_address:
                messagebox.showerror("Error", "Please enter an IP address.")
                return
            try:
                subprocess.check_output(["adb", "tcpip", "5555"])
                subprocess.check_output(["adb", "disconnect"])
                subprocess.check_output(["adb", "connect", f"{ip_address}:5555"])
                output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
                if f"{ip_address}:5555" in output:
                    messagebox.showinfo("Success", f"ADB connected over TCP/IP to {ip_address}")
                else:
                    messagebox.showerror("Error", "Failed to connect to ADB over TCP/IP. Please try again.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error connecting ADB over TCP/IP: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def disconnect_adb(self):
        def run():
            try:
                subprocess.check_output(["adb", "disconnect"])
                messagebox.showinfo("Success", "ADB disconnected from TCP/IP")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error disconnecting ADB from TCP/IP: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def get_ip_address(self):
        def run():
            try:
                # Try using 'ip addr show wlan0' first
                output = subprocess.check_output(["adb", "shell", "ip", "addr", "show", "wlan0"]).decode("utf-8")
                ip_line = [line for line in output.splitlines() if "inet " in line]
                if ip_line:
                    ip_address = ip_line[0].split()[1].split('/')[0]
                    self.ip_entry.delete(0, tk.END)
                    self.ip_entry.insert(0, ip_address)
                    return
                # Fallback to 'ifconfig wlan0' if 'ip addr show wlan0' fails
                output = subprocess.check_output(["adb", "shell", "ifconfig", "wlan0"]).decode("utf-8")
                ip_line = [line for line in output.splitlines() if "inet addr:" in line]
                if ip_line:
                    ip_address = ip_line[0].split()[1].split(':')[1]
                    self.ip_entry.delete(0, tk.END)
                    self.ip_entry.insert(0, ip_address)
                    return
                messagebox.showwarning("Warning", "Could not retrieve IP address. Ensure Wi-Fi is enabled.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error retrieving IP address: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()


