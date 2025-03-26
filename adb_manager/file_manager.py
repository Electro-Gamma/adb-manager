# file_manager.py
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import subprocess
import os
import json
import threading
from time import sleep
from PIL import Image, ImageTk  # For loading PNG icons
from .utils import execute_command, get_device_model_serial, get_connected_devices

class FileManagerPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_path = "/sdcard/"
        self.path_stack = []  # Stack to keep track of previous directories
        self.copied_paths = []  # List to store multiple copied paths
        self.row_height = 25

        # Load icon mappings from file
        self.icon_mappings = self.load_icon_mappings("./adb_manager/icon_mappings.json")

        # Load PNG icons
        self.icons = self.load_icons()

        # Style configuration for Treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=self.row_height)

        # File manager Treeview with multiple selection enabled
        self.file_manager_tree = ttk.Treeview(self, columns=("Path",), selectmode="extended")
        self.file_manager_tree.heading("#0", text="Name")
        self.file_manager_tree.heading("#1", text="Path")
        self.file_manager_tree.bind("<Double-1>", self.on_double_click)
        self.file_manager_tree.grid(row=1, column=0, columnspan=6, sticky="nsew")

        # Buttons
        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=2, column=0, padx=5, pady=5)

        self.refresh_hidden_button = ttk.Button(self, text="Refresh/.", command=self.refresh_hidden)
        self.refresh_hidden_button.grid(row=3, column=0, padx=5, pady=5)

        self.download_button = ttk.Button(self, text="Download", command=self.download)
        self.download_button.grid(row=2, column=1, padx=5, pady=5)

        self.download_all_button = ttk.Button(self, text="Download All", command=self.download_all)
        self.download_all_button.grid(row=3, column=1, padx=5, pady=5)

        self.upload_button = ttk.Button(self, text="Upload", command=self.upload)
        self.upload_button.grid(row=2, column=2, padx=5, pady=5)

        self.delete_button = ttk.Button(self, text="Delete", command=self.delete)
        self.delete_button.grid(row=3, column=2, padx=5, pady=5)

        self.mkdir_button = ttk.Button(self, text="Mkdir", command=self.mkdir)
        self.mkdir_button.grid(row=2, column=3, padx=5, pady=5)

        self.prev_dir_button = ttk.Button(self, text="Return", command=self.go_to_previous_directory)
        self.prev_dir_button.grid(row=3, column=3, padx=5, pady=5)

        self.copy_button = ttk.Button(self, text="Copy", command=self.copy)
        self.copy_button.grid(row=2, column=4, padx=5, pady=5)

        self.paste_button = ttk.Button(self, text="Paste", command=self.paste)
        self.paste_button.grid(row=3, column=4, padx=5, pady=5)

        self.compress_button = ttk.Button(self, text="Compress", command=self.compress)
        self.compress_button.grid(row=2, column=5, padx=5, pady=5)

        self.decompress_button = ttk.Button(self, text="Decompress", command=self.decompress)
        self.decompress_button.grid(row=3, column=5, padx=5, pady=5)

        # Configure row and column weights
        self.rowconfigure(1, weight=1)
        for i in range(6):
            self.columnconfigure(i, weight=1)

        # Initial refresh to load contents
        self.refresh()

    def load_icon_mappings(self, file_path):
        """Load icon mappings from a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Icon mappings file not found: {file_path}")
            return {"default": "file"}  # Fallback to default icon
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Invalid JSON in icon mappings file: {file_path}")
            return {"default": "file"}  # Fallback to default icon

    def load_icons(self):
        """Load all PNG icons from the icons folder."""
        icons = {}
        for icon_name in self.icon_mappings.values():
            icon_path = os.path.join("icons", f"{icon_name}.png")
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = icon.resize((25, 25), Image.Resampling.LANCZOS)
                icons[icon_name] = ImageTk.PhotoImage(icon)
            else:
                print(f"Warning: Icon not found for {icon_name}")
                icons[icon_name] = None

        # Ensure the "folder" icon is loaded
        folder_icon_path = os.path.join("icons", "folder.png")
        if os.path.exists(folder_icon_path):
            folder_icon = Image.open(folder_icon_path)
            folder_icon = folder_icon.resize((25, 25), Image.Resampling.LANCZOS)
            icons["folder"] = ImageTk.PhotoImage(folder_icon)
        else:
            print("Warning: Folder icon not found.")
            icons["folder"] = None

        # Ensure the "file" icon is loaded as a default
        file_icon_path = os.path.join("icons", "file.png")
        if os.path.exists(file_icon_path):
            file_icon = Image.open(file_icon_path)
            file_icon = file_icon.resize((25, 25), Image.Resampling.LANCZOS)
            icons["file"] = ImageTk.PhotoImage(file_icon)
        else:
            print("Warning: File icon not found.")
            icons["file"] = None

        return icons

    def get_file_icon(self, filename):
        """Get the icon for a file based on its extension."""
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        icon_name = self.icon_mappings.get(ext, self.icon_mappings.get("default", "file"))
        return self.icons.get(icon_name)

    def insert_sorted_items(self, files):
        folders = []
        files_list = []

        for file in files:
            if file.endswith('/'):
                folders.append(file[:-1])  # Remove the trailing `/`
            else:
                files_list.append(file)

        # Sort folders and files alphabetically
        folders.sort(key=lambda x: x.lower())
        files_list.sort(key=lambda x: x.lower())

        # Insert folders first
        for folder in folders:
            self.file_manager_tree.insert("", "end", text=folder, values=(self.current_path,), image=self.icons.get("folder"))

        # Insert files next
        for file in files_list:
            icon = self.get_file_icon(file)
            if icon is None:
                icon = self.icons.get("file")  # Use default icon if no specific icon is found
            self.file_manager_tree.insert("", "end", text=file, values=(self.current_path,), image=icon)

    def on_double_click(self, event):
        item = self.file_manager_tree.selection()[0]
        path = self.file_manager_tree.item(item, "text")
        full_path = f'"{self.current_path}/{path}"'.replace('//', '/')  # Quote the path
        if self.check_if_directory(full_path):
            self.path_stack.append(self.current_path)  # Push current path to stack
            self.current_path = full_path.strip('"')  # Update current path (remove quotes)
            self.refresh()  # Refresh Treeview
        else:
            messagebox.showerror("Error", "Selected item is not a directory.")

    def go_to_previous_directory(self):
        if self.path_stack:  # Check if there are previous directories in the stack
            previous_path = self.path_stack.pop()  # Pop the previous path
            self.current_path = previous_path  # Update current path
            self.refresh()  # Refresh Treeview
        else:
            messagebox.showinfo("Info", "No previous directory available.")

    def refresh(self):
        def run():
            self.file_manager_tree.delete(*self.file_manager_tree.get_children())
            try:
                # Use `ls -p` to append `/` to directories
                output = subprocess.check_output(
                    ["adb", "shell", "ls", "-p", f'"{self.current_path}"'],  # Quote the path
                    universal_newlines=True, encoding="utf-8"
                )
                files = output.splitlines()
                self.insert_sorted_items(files)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def refresh_hidden(self):
        def run():
            self.file_manager_tree.delete(*self.file_manager_tree.get_children())
            try:
                # Use `ls -ap` to include hidden files and append `/` to directories
                output = subprocess.check_output(
                    ["adb", "shell", "ls", "-ap", f'"{self.current_path}"'],  # Quote the path
                    universal_newlines=True, encoding="utf-8"
                )
                files = output.splitlines()
                self.insert_sorted_items(files)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error: {e}")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def check_if_directory_compress(self, path):
        """Check if the given path is a directory."""
        try:
            # Use `-d` flag to check if the path is a directory, and quote the path
            subprocess.check_output(["adb", "shell", "test", "-d", f'"{path}"'], stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def check_if_directory(self, path):
        try:
            # Use `-d` flag to check if the path is a directory
            subprocess.check_output(["adb", "shell", "test", "-d", path], stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    def check_if_file(self, path):
        """Check if the given path is a file."""
        try:
            # Use `-f` flag to check if the path is a file, and quote the path
            subprocess.check_output(["adb", "shell", "test", "-f", f'"{path}"'], stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    def delete(self):
        def run():
            selected_items = self.file_manager_tree.selection()  # Get all selected items
            if not selected_items:
                messagebox.showwarning("No Selection", "Please select one or more items to delete.")
                return

            for item in selected_items:
                path = self.file_manager_tree.item(item, "text")
                full_path = os.path.join(self.current_path, path).replace('\\', '/')
                try:
                    subprocess.check_call(["adb", "shell", "rm", "-r", f'"{full_path}"'])
                    messagebox.showinfo("Success", f"{path} deleted successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error deleting {path}: {e}")

            self.refresh()  # Refresh the file list after deletion

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def download(self):
        def run():
            device_identifier = 1
            device_model, device_serial = get_device_model_serial(device_identifier)
            if device_model and device_serial:
                selected_items = self.file_manager_tree.selection()  # Get all selected items
                if not selected_items:
                    messagebox.showwarning("No Selection", "Please select one or more items to download.")
                    return

                for item in selected_items:
                    path = self.file_manager_tree.item(item, "text")
                    try:
                        os.makedirs(f"./device-pull/{device_model.replace(':', '_').replace('.', '_')}-{device_serial.replace(':', '_').replace('.', '_')}", exist_ok=True)
                        file_path = os.path.join(self.current_path, path).replace('\\', '/')

                        # Get the total size of the file/folder in MB
                        total_size_kb = self.get_remote_file_size_kb(device_serial, file_path)
                        if total_size_kb == 0:
                            messagebox.showerror("Error", f"Failed to get file size for {path}.")
                            continue

                        total_size_mb = total_size_kb / 1024  # Convert KB to MB

                        # Create a progress window
                        progress_window = tk.Toplevel(self)
                        progress_window.title(f"Download Progress - {path}")
                        progress_label = ttk.Label(progress_window, text=f"Downloading {path}...")
                        progress_label.pack(pady=10)
                        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", maximum=100)
                        progress_bar.pack(pady=10)

                        # Function to update progress
                        def update_progress():
                            while not download_complete:
                                # Get the current size of the downloaded file in MB
                                downloaded_size_kb = self.get_local_file_size_kb(f"./device-pull/{device_model.replace(':', '_').replace('.', '_')}-{device_serial.replace(':', '_').replace('.', '_')}/{path}")
                                downloaded_size_mb = downloaded_size_kb / 1024  # Convert KB to MB

                                # Cap the progress at 100%
                                progress_percent = min(int((downloaded_size_mb / total_size_mb) * 100), 100)
                                progress_bar["value"] = progress_percent
                                progress_label.config(text=f"Downloading {path}... [{progress_percent}%] ({min(downloaded_size_mb, total_size_mb):.2f} MB / {total_size_mb:.2f} MB)")
                                progress_window.update()
                                sleep(0.5)

                        # Start the download in a separate thread
                        download_complete = False
                        progress_thread = threading.Thread(target=update_progress)
                        progress_thread.start()

                        # Perform the download
                        subprocess.check_call(["adb", "-s", device_serial, "pull", file_path, f"./device-pull/{device_model.replace(':', '_').replace('.', '_')}-{device_serial.replace(':', '_').replace('.', '_')}/{path}"])
                        download_complete = True
                        progress_thread.join()

                        # Close the progress window
                        progress_window.destroy()
                        messagebox.showinfo("Success", f"{path} downloaded successfully!")
                    except subprocess.CalledProcessError as e:
                        messagebox.showerror("Error", f"Error downloading {path}: {e}")
            else:
                messagebox.showerror("Error", "Failed to get device model and serial number.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def download_all(self):
        def run():
            device_identifier = 1
            device_model, device_serial = get_device_model_serial(device_identifier)
            if device_model and device_serial:
                try:
                    sanitized_model = device_model.replace(":", "_").replace(".", "_")
                    sanitized_serial = device_serial.replace(":", "_").replace(".", "_")
                    os.makedirs(f"./device-pull/{sanitized_model}-{sanitized_serial}", exist_ok=True)

                    # Get the total size of the /sdcard directory in MB
                    total_size_kb = self.get_remote_file_size_kb(device_serial, "/sdcard/")
                    if total_size_kb == 0:
                        messagebox.showerror("Error", "Failed to get directory size.")
                        return
                    total_size_mb = total_size_kb / 1024  # Convert KB to MB

                    # Create a progress window
                    progress_window = tk.Toplevel(self)
                    progress_window.title("Download Progress")
                    progress_label = ttk.Label(progress_window, text="Downloading all files from /sdcard...")
                    progress_label.pack(pady=10)
                    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", maximum=100)
                    progress_bar.pack(pady=10)

                    # Function to update progress
                    def update_progress():
                        while not download_complete:
                            # Get the current size of the downloaded files in MB
                            downloaded_size_kb = self.get_local_file_size_kb(f"./device-pull/{sanitized_model}-{sanitized_serial}")
                            downloaded_size_mb = downloaded_size_kb / 1024  # Convert KB to MB

                            # Cap the progress at 100%
                            progress_percent = min(int((downloaded_size_mb / total_size_mb) * 100), 100)
                            progress_bar["value"] = progress_percent
                            progress_label.config(text=f"Downloading /sdcard... [{progress_percent}%] ({min(downloaded_size_mb, total_size_mb):.2f} MB / {total_size_mb:.2f} MB)")
                            progress_window.update()
                            sleep(0.5)

                    # Start the download in a separate thread
                    download_complete = False
                    progress_thread = threading.Thread(target=update_progress)
                    progress_thread.start()

                    # Perform the download
                    subprocess.check_call(["adb", "-s", device_serial, "pull", "/sdcard/", f"./device-pull/{sanitized_model}-{sanitized_serial}/"])
                    download_complete = True
                    progress_thread.join()

                    # Close the progress window
                    progress_window.destroy()
                    messagebox.showinfo("Success", "All data from /sdcard downloaded successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Error: {e}")
            else:
                messagebox.showerror("Error", "Failed to get device model and serial number.")

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()
        
    def copy(self):
        selected_items = self.file_manager_tree.selection()  # Get all selected items
        if selected_items:
            self.copied_paths = []  # Store multiple copied paths
            for item in selected_items:
                path = self.file_manager_tree.item(item, "text")
                full_path = os.path.join(self.current_path, path).replace('\\', '/')
                self.copied_paths.append(full_path)
            print(f"Copied paths: {self.copied_paths}")

    def paste(self):
        def run():
            if hasattr(self, "copied_paths") and self.copied_paths:
                for copied_path in self.copied_paths:
                    destination_path = os.path.join(self.current_path, os.path.basename(copied_path)).replace('\\', '/')
                    try:
                        subprocess.check_call(["adb", "shell", "cp", "-r", f'"{copied_path}"', f'"{destination_path}"'])
                    except subprocess.CalledProcessError as e:
                        messagebox.showerror("Error", f"Error copying {copied_path}: {e}")
                self.refresh()  # Refresh the file list after pasting

        # Start the operation in a separate thread
        thread = threading.Thread(target=run)
        thread.start()

    def mkdir(self):
        new_dir_name = simpledialog.askstring("Create Directory", "Enter new directory name:")
        if new_dir_name:
            full_path = os.path.join(self.current_path, new_dir_name).replace('\\', '/')
            try:
                subprocess.check_call(["adb", "shell", "mkdir", f'"{full_path}"'])
                messagebox.showinfo("Success", f"Directory '{new_dir_name}' created successfully!")
                self.refresh()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error: {e}")

    def get_remote_file_size_kb(self, device_serial, remote_path):
        """Get the size of a file or folder on the remote device in KB."""
        try:
            # Use `du -ks` to get the size in KB
            output = subprocess.check_output(
                ["adb", "-s", device_serial, "shell", "du", "-s", f'"{remote_path}"'],
                universal_newlines=True
            )
            size_kb = int(output.split()[0])  # Size in KB
            return size_kb
        except subprocess.CalledProcessError:
            return 0

    def get_local_file_size_kb(self, local_path):
        """Get the size of a file or folder on the local machine in KB."""
        if os.path.isfile(local_path):
            return os.path.getsize(local_path) / 1024  # Convert bytes to KB
        elif os.path.isdir(local_path):
            total_size_bytes = 0
            for dirpath, _, filenames in os.walk(local_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size_bytes += os.path.getsize(fp)
            return total_size_bytes / 1024  # Convert bytes to KB
        else:
            return 0

    def upload(self):
        # Ask the user if they want to upload a folder or files
        choice = messagebox.askyesno("Upload", "Do you want to upload a folder? (No for files)")
        
        if choice:  # User wants to upload a folder
            folder_path = filedialog.askdirectory(initialdir="/", title="Select folder to upload")
            if folder_path:
                # If no item is selected, default to the current directory
                if not self.file_manager_tree.selection():
                    destination_path = self.current_path
                else:
                    # If an item is selected, use its path as the destination
                    selected_item = self.file_manager_tree.selection()[0]
                    selected_path = self.file_manager_tree.item(selected_item, "text")
                    destination_path = os.path.join(self.current_path, selected_path).replace('\\', '/')

                # Start the folder upload in a separate thread
                threading.Thread(target=self.upload_folder, args=(folder_path, destination_path)).start()
        else:  # User wants to upload files
            file_paths = filedialog.askopenfilenames(initialdir="/", title="Select files to upload")
            if file_paths:
                # If no item is selected, default to the current directory
                if not self.file_manager_tree.selection():
                    destination_path = self.current_path
                else:
                    # If an item is selected, use its path as the destination
                    selected_item = self.file_manager_tree.selection()[0]
                    selected_path = self.file_manager_tree.item(selected_item, "text")
                    destination_path = os.path.join(self.current_path, selected_path).replace('\\', '/')

                # Start the file upload in a separate thread
                threading.Thread(target=self.upload_files, args=(file_paths, destination_path)).start()

    def upload_folder(self, folder_path, destination_path):
        """Upload a folder (and its contents) to the device in a separate thread."""
        try:
            # Upload the folder and its contents to the destination path
            subprocess.check_call(["adb", "push", folder_path, destination_path])
            messagebox.showinfo("Success", "Folder uploaded successfully!")
            self.refresh()  # Refresh the file list after upload
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error uploading folder: {e}")

    def upload_files(self, file_paths, destination_path):
        """Upload multiple files to the device in a separate thread."""
        try:
            for file_path in file_paths:
                # Upload each file to the destination path
                subprocess.check_call(["adb", "push", file_path, destination_path])
            messagebox.showinfo("Success", "All files uploaded successfully!")
            self.refresh()  # Refresh the file list after upload
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error uploading files: {e}")

    def compress(self):
        """Compress a selected folder or file on the device."""
        selected_item = self.file_manager_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file or folder to compress.")
            return

        item = selected_item[0]
        path = self.file_manager_tree.item(item, "text")
        full_path = os.path.join(self.current_path, path).replace('\\', '/')

        # Check if the selected item is a directory or file
        if not self.check_if_directory_compress(full_path) and not self.check_if_file(full_path):
            messagebox.showerror("Error", "Selected item is neither a file nor a directory.")
            return

        # Get the size of the folder/file
        size_kb = self.get_remote_file_size_kb(get_connected_devices()[0], full_path)
        if size_kb == 0:
            messagebox.showerror("Error", "Failed to get size of the selected item.")
            return

        # Convert size to the appropriate unit
        if size_kb < 1000:  # Less than 1000 KB
            size_str = f"{size_kb:.2f} KB"
        elif size_kb < 1000 * 1000:  # Less than 1000 MB
            size_mb = size_kb / 1024  # Convert KB to MB
            size_str = f"{size_mb:.2f} MB"
        else:  # Greater than or equal to 1000 MB
            size_gb = size_kb / (1024 * 1024)  # Convert KB to GB
            size_str = f"{size_gb:.2f} GB"

        # Ask for confirmation with the size in the appropriate unit
        confirm = messagebox.askyesno(
            "Confirm Compression",
            f"The selected item is {size_str}. Do you want to compress it?"
        )
        if not confirm:
            return

        # Ask for the output file name
        output_file = simpledialog.askstring(
            "Compress",
            "Enter the output file name (e.g., myfiles.tar.gz):",
            initialvalue=f"{path}.tar.gz"
        )
        if not output_file:
            return

        output_path = os.path.join(self.current_path, output_file).replace('\\', '/')

        # Perform the compression
        def run_compression():
            try:
                if self.check_if_directory_compress(full_path):
                    # Compress a directory
                    command = [
                        "adb", "shell",
                        "tar", "-czf", f'"{output_path}"', "-C", f'"{os.path.dirname(full_path)}"', f'"{os.path.basename(full_path)}"'
                    ]
                else:
                    # Compress a single file
                    command = [
                        "adb", "shell",
                        "tar", "-czf", f'"{output_path}"', "-C", f'"{os.path.dirname(full_path)}"', f'"{os.path.basename(full_path)}"'
                    ]

                # Run the command using subprocess.check_call
                subprocess.check_call(command)
                messagebox.showinfo("Success", f"Compression completed: {output_path}")
                self.refresh()  # Refresh the file list
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error during compression: {e}")

        # Run the compression in a separate thread
        thread = threading.Thread(target=run_compression)
        thread.start()

    def decompress(self):
        """Decompress a selected .tar.gz or .tar file on the device."""
        selected_item = self.file_manager_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a .tar.gz or .tar file to decompress.")
            return

        item = selected_item[0]
        path = self.file_manager_tree.item(item, "text")
        full_path = os.path.join(self.current_path, path).replace('\\', '/')

        # Check if the selected item is a .tar.gz or .tar file
        if not (full_path.endswith(".tar.gz") or full_path.endswith(".tar")):
            messagebox.showerror("Error", "Selected item is not a .tar.gz or .tar file.")
            return

        # Get the size of the file
        size_kb = self.get_remote_file_size_kb(get_connected_devices()[0], full_path)
        if size_kb == 0:
            messagebox.showerror("Error", "Failed to get size of the selected item.")
            return

        # Convert size to the appropriate unit
        if size_kb < 1000:  # Less than 1000 KB
            size_str = f"{size_kb:.2f} KB"
        elif size_kb < 1000 * 1000:  # Less than 1000 MB
            size_mb = size_kb / 1024  # Convert KB to MB
            size_str = f"{size_mb:.2f} MB"
        else:  # Greater than or equal to 1000 MB
            size_gb = size_kb / (1024 * 1024)  # Convert KB to GB
            size_str = f"{size_gb:.2f} GB"

        # Ask for confirmation with the size in the appropriate unit
        confirm = messagebox.askyesno(
            "Confirm Decompression",
            f"The selected item is {size_str}. Do you want to decompress it?"
        )
        if not confirm:
            return

        # Ask for the output directory
        output_dir = simpledialog.askstring(
            "Decompress",
            "Enter the output directory (e.g., /sdcard/extracted):",
            initialvalue=os.path.dirname(full_path)
        )
        if not output_dir:
            return

        # Perform the decompression
        def run_decompression():
            try:
                # Create the output directory if it doesn't exist
                subprocess.check_call(["adb", "shell", "mkdir", "-p", f'"{output_dir}"'])

                # Decompress the file
                command = [
                    "adb", "shell",
                    "tar", "-xzf", f'"{full_path}"', "-C", f'"{output_dir}"'
                ]
                subprocess.check_call(command)
                messagebox.showinfo("Success", f"Decompression completed to: {output_dir}")
                self.refresh()  # Refresh the file list
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error during decompression: {e}")

        # Run the decompression in a separate thread
        thread = threading.Thread(target=run_decompression)
        thread.start()

