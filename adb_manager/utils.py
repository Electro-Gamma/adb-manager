# utils.py
import subprocess
import os
from datetime import datetime
from time import sleep
from tkinter import messagebox
import threading

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate()
    return output.decode().strip()

def get_connected_devices():
    adb_devices_output = execute_command("adb devices").split('\n')[1:]
    devices = [line.split('\t')[0] for line in adb_devices_output if line.strip()]
    return devices

def get_device_info(device_serial):
    info = {}
    info['model'] = execute_command(f"adb -s {device_serial} shell getprop ro.product.model")
    info['brand'] = execute_command(f"adb -s {device_serial} shell getprop ro.product.vendor.brand")
    info['chipset'] = execute_command(f"adb -s {device_serial} shell getprop ro.product.board")
    info['android_version'] = execute_command(f"adb -s {device_serial} shell getprop ro.build.version.release")
    info['security_patch'] = execute_command(f"adb -s {device_serial} shell getprop ro.build.version.security_patch")
    info['device'] = execute_command(f"adb -s {device_serial} shell getprop ro.product.vendor.device")
    info['sim'] = execute_command(f"adb -s {device_serial} shell getprop gsm.sim.operator.alpha")
    info['encryption_state'] = execute_command(f"adb -s {device_serial} shell getprop ro.crypto.state")
    info['build_date'] = execute_command(f"adb -s {device_serial} shell getprop ro.build.date")
    info['sdk_version'] = execute_command(f"adb -s {device_serial} shell getprop ro.build.version.sdk")
    info['wifi_interface'] = execute_command(f"adb -s {device_serial} shell getprop wifi.interface")
    info['abi'] = execute_command(f"adb -s {device_serial} shell getprop ro.product.cpu.abi")
    return info

def capture_screenshot(device_serial):
    def run():
        device_model = execute_command(f"adb -s {device_serial} shell getprop ro.product.model")
        if device_model:
            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            adb_command = ["adb", "-s", device_serial, "shell", "screencap", "-p", f"/sdcard/screenshot-{current_time}.png"]
            subprocess.run(adb_command, check=True)
            sanitized_model = device_model.replace(":", "_").replace(".", "_")
            sanitized_serial = device_serial.replace(":", "_").replace(".", "_")
            directory_path = f"./device-pull/{sanitized_model}-{sanitized_serial}"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            screenshot_folder_path = os.path.join(directory_path, "screenshot")
            if not os.path.exists(screenshot_folder_path):
                os.makedirs(screenshot_folder_path)
            adb_command = ["adb", "-s", device_serial, "pull", f"/sdcard/screenshot-{current_time}.png", screenshot_folder_path]
            subprocess.run(adb_command, check=True)
            adb_command = ["adb", "-s", device_serial, "shell", "rm", f"/sdcard/screenshot-{current_time}.png"]
            subprocess.run(adb_command, check=True)
            print("Screenshot process complete.")
        else:
            print("Device model not found.")

    # Start the operation in a separate thread
    thread = threading.Thread(target=run)
    thread.start()

def capture_screenrecord(device_serial):
    global is_recording
    device_model = execute_command(f"adb -s {device_serial} shell getprop ro.product.model")
    if device_model:
        try:
            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"screenrecord-{current_time}.mp4"
            adb_command = ["adb", "-s", device_serial, "shell", "screenrecord", f"/sdcard/{filename}"]
            subprocess.Popen(adb_command)
            is_recording = True
            messagebox.showinfo("Screen Recording Started", "Screen recording started successfully.")
            return device_model, filename
        except subprocess.CalledProcessError as e:
            print("Error:", e)
    else:
        print("Device model not found.")
        return None, None

def stop_screenrecord(device_serial, device_model, filename):
    global is_recording
    try:
        if is_recording:
            adb_command = ["adb", "-s", device_serial, "shell", "pkill", "-l", "2", "screenrecord"]
            subprocess.run(adb_command, check=True)
            sleep(0.5)
            is_recording = False
            directory_path = f"./device-pull/{device_model}-{device_serial}"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            screenrecord_folder_path = os.path.join(directory_path, "screenrecord")
            if not os.path.exists(screenrecord_folder_path):
                os.makedirs(screenrecord_folder_path)
            adb_command = ["adb", "-s", device_serial, "pull", f"/sdcard/{filename}", screenrecord_folder_path]
            subprocess.run(adb_command, check=True)
            adb_command = ["adb", "-s", device_serial, "shell", "rm", f"/sdcard/{filename}"]
            subprocess.run(adb_command, check=True)
            messagebox.showinfo("Screen Recording Stopped", "Screen recording stopped and saved successfully.")
        else:
            messagebox.showwarning("Screen Recording Not Active", "No screen recording is currently active.")
    except subprocess.CalledProcessError as e:
        messagebox.showwarning("Screen Recording File Not Found", "The screen recording file does not exist on the device.")
    except Exception as e:
        print("Error:", e)

def get_device_model_serial(device_identifier):
    if isinstance(device_identifier, int):
        devices = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout.strip().split('\n')[1:]
        if len(devices) >= device_identifier:
            device_serial = devices[device_identifier - 1].split('\t')[0]
            device_model = subprocess.run(["adb", "-s", device_serial, "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
            return device_model, device_serial
        else:
            return None, None
    elif isinstance(device_identifier, str):
        device_serial = device_identifier
        device_model = subprocess.run(["adb", "-s", device_serial, "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
        return device_model, device_serial
    else:
        return None, None

def format_package_info(package_info):
    formatted_info = []
    entries = package_info.split("|")[1:]  # Remove empty strings before and after entries

    for entry in entries:
        parts = entry.split("\\+")
        if len(parts) == 2:
            package_name, app_name = parts
            app_name = app_name.strip().lstrip("\\")
            formatted_entry = {
                "package_name": package_name.strip(),
                "app_name": app_name.strip()
            }
            formatted_info.append(formatted_entry)
        else:
            print(f"Skipping invalid entry: {entry}")

    return sorted(formatted_info, key=lambda x: x['package_name'].lower())