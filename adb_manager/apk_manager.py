# apk_manager.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading  # Import threading module
from PIL import Image, ImageTk
from .utils import format_package_info, get_device_model_serial
import zipfile
from time import sleep

class APKManagerPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.package_icons = {}
        self.row_height = 60
        self.formatted_info = None

        # Search Bar and Buttons Frame
        self.search_frame = ttk.Frame(self)
        self.search_frame.pack(fill=tk.X, pady=5)


        # Refresh Button
        self.refresh_button = ttk.Button(self.search_frame, text="Refresh", command=self.refresh_package_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        # Update Button
        self.update_button = ttk.Button(self.search_frame, text="Update", command=self.setup_acbridge)
        self.update_button.pack(side=tk.LEFT, padx=5)
        # Search Entry
        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        # Search Button
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_apk)
        self.search_button.pack(side=tk.LEFT, padx=5)
        # Clear Search Button
        self.clear_search_button = ttk.Button(self.search_frame, text="Clear", command=self.clear_search)
        self.clear_search_button.pack(side=tk.LEFT, padx=5)

        # Treeview for APK List
        self.style = ttk.Style()
        self.style.configure("Custom.Treeview", rowheight=self.row_height)

        self.package_tree = ttk.Treeview(self, columns=("Package", "App Name"), height=5, style="Custom.Treeview")
        self.package_tree.heading("#0", text="App Icon")
        self.package_tree.heading("#1", text="App Name")
        self.package_tree.heading("#2", text="Package")
        self.package_tree.pack(fill=tk.BOTH, expand=True)

        self.package_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.package_tree.yview)
        self.package_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.package_tree.configure(yscrollcommand=self.package_scrollbar.set)

        # Buttons Frame (Footer)
        self.button_frame_1 = ttk.Frame(self)
        self.button_frame_1.pack(fill=tk.X, pady=10)

        # Buttons Frame (Footer)
        self.button_frame_2 = ttk.Frame(self)
        self.button_frame_2.pack(fill=tk.X, pady=10)
        
        # First Row: 5 Buttons (Left to Right)
        self.enable_button = ttk.Button(self.button_frame_1, text="Enable", command=self.enable_package, state=tk.DISABLED)
        self.enable_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.disable_button = ttk.Button(self.button_frame_1, text="Disable", command=self.disable_package, state=tk.DISABLED)
        self.disable_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.clear_data_button = ttk.Button(self.button_frame_1, text="Clear App Data", command=self.clear_app_data, state=tk.DISABLED)
        self.clear_data_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.uninstall_button = ttk.Button(self.button_frame_1, text="Uninstall", command=self.uninstall_package, state=tk.DISABLED)
        self.uninstall_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.save_button = ttk.Button(self.button_frame_1, text="Extract APK", command=self.save_actions, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Second Row: 2 Buttons (Left to Right)
        self.launch_app_button = ttk.Button(self.button_frame_2, text="Launch App", command=self.launch_app, state=tk.DISABLED)
        self.launch_app_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.install_apk_button = ttk.Button(self.button_frame_2, text="Install APK", command=self.install_apk)
        self.install_apk_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        

        self.package_tree.bind("<<TreeviewSelect>>", self.on_select_package)

    def install_apk(self):
        filepath = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
        if filepath:
            def run():
                try:
                    subprocess.check_call(["adb", "install", filepath])
                    messagebox.showinfo("Success", "APK installed successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error installing APK: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def resize_image(self, image_path, width, height):
        image = Image.open(image_path)
        resized_image = image.resize((width, height))
        return ImageTk.PhotoImage(resized_image)

    def search_apk(self):
        """Filter the APK list based on the search query."""
        search_query = self.search_entry.get().strip().lower()
        if not search_query:
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return

        # Clear the current treeview
        self.package_tree.delete(*self.package_tree.get_children())

        # Filter packages based on the search query
        for package_name, app_name in self.package_to_app.items():
            if search_query in app_name.lower():
                icon_path = f"./tools/ACBridge/icons/{package_name}.png"
                if os.path.exists(icon_path):
                    resized_icon = self.resize_image(icon_path, 50, 50)
                    self.package_icons[package_name] = resized_icon
                    self.package_tree.insert("", "end", values=(app_name, package_name), image=resized_icon)
                else:
                    self.package_tree.insert("", "end", values=(app_name, package_name))

    def clear_search(self):
        """Clear the search and show the full list of APKs."""
        self.search_entry.delete(0, tk.END)
        self.refresh_package_list()

    def refresh_package_list(self):
        """Refresh the list of installed packages."""
        def run():
            self.package_tree.delete(*self.package_tree.get_children())
            try:
                output = subprocess.check_output(["adb", "shell", "pm", "list", "packages"], universal_newlines=True)
                packages = output.strip().split('\n')
                package_names = [package.split(':')[1] for package in packages]

                formatted_info = None
                file_path = "./tools/ACBridge/acbridge"
                with open(file_path, "r", encoding="utf-8") as file:
                    input_string = file.read()
                    formatted_info = format_package_info(input_string)

                self.package_to_app = {entry['package_name']: entry['app_name'] for entry in formatted_info}
                sorted_package_names = sorted(package_names, key=lambda x: self.package_to_app.get(x, '').lower())

                for package_name in sorted_package_names:
                    app_name = self.package_to_app.get(package_name, None)
                    icon_path = f"./tools/ACBridge/icons/{package_name}.png"
                    if os.path.exists(icon_path):
                        resized_icon = self.resize_image(icon_path, 50, 50)
                        self.package_icons[package_name] = resized_icon
                        self.package_tree.insert("", "end", values=(app_name, package_name), image=resized_icon)
                    else:
                        if app_name:
                            self.package_tree.insert("", "end", values=(app_name, package_name))
                        else:
                            self.package_tree.insert("", "end", values=(package_name,))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def on_select_package(self, event):
        selected_item = self.package_tree.selection()
        if selected_item:
            self.enable_button.config(state=tk.NORMAL)
            self.disable_button.config(state=tk.NORMAL)
            self.clear_data_button.config(state=tk.NORMAL)
            self.uninstall_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.launch_app_button.config(state=tk.NORMAL)
        else:
            self.enable_button.config(state=tk.DISABLED)
            self.disable_button.config(state=tk.DISABLED)
            self.clear_data_button.config(state=tk.DISABLED)
            self.uninstall_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.launch_app_button.config(state=tk.DISABLED)

    def enable_package(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    subprocess.check_call(["adb", "shell", "pm", "enable", "--user", "0", package_name])
                    messagebox.showinfo("Success", f"Package {package_name} enabled successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error enabling package {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def disable_package(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    subprocess.check_call(["adb", "shell", "pm", "disable-user", "--user", "0", package_name])
                    messagebox.showinfo("Success", f"Package {package_name} disabled successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error disabling package {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def clear_app_data(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    subprocess.check_call(["adb", "shell", "pm", "clear", "--user", "0", package_name])
                    messagebox.showinfo("Success", f"App data cleared for package {package_name}!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error clearing app data for package {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def uninstall_package(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    subprocess.check_call(["adb", "shell", "pm", "uninstall", "--user", "0", package_name])
                    messagebox.showinfo("Success", f"Package {package_name} uninstalled successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error uninstalling package {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def save_actions(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    output = subprocess.check_output(["adb", "shell", "pm", "path", package_name], universal_newlines=True)
                    path = output.split(":")[1].strip()
                    device_model, device_serial = get_device_model_serial(0)
                    if device_model and device_serial:
                        sanitized_model = device_model.replace(":", "_").replace(".", "_")
                        sanitized_serial = device_serial.replace(":", "_").replace(".", "_")
                        os.makedirs(f"./device-pull/{sanitized_model}-{sanitized_serial}/Downloadapk", exist_ok=True)
                        subprocess.check_call(["adb", "shell", "cp", "-r", path, f"/storage/emulated/0/{package_name}.apk"])
                        subprocess.check_call(["adb", "pull", f"/storage/emulated/0/{package_name}.apk", f"./device-pull/{sanitized_model}-{sanitized_serial}/Downloadapk/{package_name}.apk"])
                        subprocess.check_call(["adb", "shell", "rm", f"/storage/emulated/0/{package_name}.apk"])
                        messagebox.showinfo("Success", f"APK for package {package_name} saved successfully!")
                    else:
                        os.makedirs(f"./device-pull/{device_model}-{device_serial}/Downloadapk", exist_ok=True)
                        subprocess.check_call(["adb", "shell", "cp", "-r", path, f"/storage/emulated/0/{package_name}.apk"])
                        subprocess.check_call(["adb", "pull", f"/storage/emulated/0/{package_name}.apk", f"./device-pull/{device_model}-{device_serial}/Downloadapk/{package_name}.apk"])
                        subprocess.check_call(["adb", "shell", "rm", f"/storage/emulated/0/{package_name}.apk"])
                        messagebox.showinfo("Success", f"APK for package {package_name} saved successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error saving APK for package {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()

    def launch_app(self):
        selected_item = self.package_tree.selection()
        if selected_item:
            package_name = self.package_tree.item(selected_item, "values")[1]
            def run():
                try:
                    subprocess.check_call(["adb", "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
                    messagebox.showinfo("Success", f"Successfully launched {package_name}!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error launching {package_name}: {e}")

            # Start the operation in a separate thread
            thread = threading.Thread(target=run)
            thread.start()
        else:
            messagebox.showerror("Error", "No package selected!")

    def setup_acbridge(self):
        package_name = "com.cybercat.acbridge"
        activity_name = ".MainActivity"
        icons_destination_path = "./tools/ACBridge/icons"
        acbridge_destination_path = "./tools/ACBridge/"

        def check_acbridge_installed(package_name):
            check_command = f"adb shell pm list packages {package_name}"
            result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
            return package_name in result.stdout

        def run():
            if not check_acbridge_installed(package_name):
                apk_path = "./tools/ACBridge/acbridge.apk"
                install_command = f"adb install {apk_path}"
                os.system(install_command)
                sleep(1)

                mkdir_command = f"adb shell mkdir -p /storage/emulated/0/.adac"
                os.system(mkdir_command)

                remove_settings_command = f"adb shell rm /storage/emulated/0/.adac/settings"
                os.system(remove_settings_command)

                push_settings_command = f"adb push ./tools/ACBridge/settings /storage/emulated/0/.adac"
                os.system(push_settings_command)

                write_permission_command = f"adb shell pm grant {package_name} android.permission.WRITE_EXTERNAL_STORAGE"
                os.system(write_permission_command)
                sleep(1)

                usage_stats_permission_command = f"adb shell pm grant {package_name} android.permission.PACKAGE_USAGE_STATS"
                os.system(usage_stats_permission_command)
                sleep(1)

                launch_command = f"adb shell am start -n {package_name}/{activity_name}"
                os.system(launch_command)
                sleep(20)

                launch_command = f"adb shell am start -n {package_name}/{activity_name}"
                os.system(launch_command)
                sleep(20)
            else:
                launch_command = f"adb shell am start -n {package_name}/{activity_name}"
                os.system(launch_command)
                sleep(20)

            pull_icons_command = "adb pull /storage/emulated/0/.adac/icons.zip ./tools/ACBridge/"
            os.system(pull_icons_command)

            pull_acbridge_command = "adb pull /storage/emulated/0/.adac/.acbridge ./tools/ACBridge/acbridge"
            os.system(pull_acbridge_command)

            pull_sizes_command = "adb pull /storage/emulated/0/.adac/.sizes ./tools/ACBridge/sizes"
            os.system(pull_sizes_command)

            with zipfile.ZipFile("./tools/ACBridge/icons.zip", "r") as zip_ref:
                zip_ref.extractall(icons_destination_path)

            self.refresh_package_list()
            messagebox.showinfo("Update Data", "Data has been updated successfully!")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()
