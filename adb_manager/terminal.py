# terminal.py
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import platform
import threading
import time
import signal

class TerminalPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Terminal frame
        self.terminal_frame = ttk.Frame(self)
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)

        # Terminal text widget
        self.terminal_text = tk.Text(
            self.terminal_frame,
            wrap="word",
            width=40,
            height=10,
            bg="black",  # Black background
            fg="#00FF00",  # Green text
            insertbackground="#00FF00",  # Green cursor
            font=("Consolas", 10),  # Monospaced font
            borderwidth=0,
            highlightthickness=0
        )
        self.terminal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind left-click release to copy text
        self.terminal_text.bind("<ButtonRelease-1>", self.copy_selected_text)
        # Scrollbar for the terminal
        self.scrollbar = tk.Scrollbar(
            self.terminal_frame,
            orient="vertical",
            command=self.terminal_text.yview,
            bg="black",  # Black background
            troughcolor="black",  # Black trough
            activebackground="#00FF00"  # Green when active
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.configure(yscrollcommand=self.scrollbar.set)

        # Command history and entry
        self.command_history = []
        self.command_index = 0
        self.command_entry = ttk.Entry(
            self,
            width=50,
            font=("Arial", 10)
        )
        self.command_entry.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.bind("<Up>", self.navigate_history)
        self.command_entry.bind("<Down>", self.navigate_history)

        # Button frame to hold Clear and CTRL+C buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, pady=5)

        # Clear button
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear",
            command=self.clear_terminal
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # CTRL+C button
        self.ctrl_c_button = ttk.Button(
            self.button_frame,
            text="CTRL+C",
            command=self.send_ctrl_c
        )
        self.ctrl_c_button.pack(side=tk.LEFT, padx=5)

        # Process handle for the currently running command
        self.current_process = None

    def execute_command(self, event=None):
        """Execute the command entered in the terminal."""
        command = self.command_entry.get().strip()
        if command:
            self.command_history.append(command)
            self.command_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)

            # Handle special commands
            if command.strip() == "clear":
                self.clear_terminal()
            elif command.startswith("cd "):
                self.change_directory(command)
            elif command.strip() == "adb shell":
                self.start_adb_shell()
            elif command.strip() == "ls":
                self.list_directory()  # Handle 'ls' command using Python's os module
            else:
                # Run the command in a separate thread with real-time output
                threading.Thread(target=self.run_command_with_realtime_output, args=(command,), daemon=True).start()

    def list_directory(self):
        """List files and directories in the current directory using Python's os module."""
        try:
            current_dir = os.getcwd()
            files_and_dirs = os.listdir(current_dir)
            output = "\n".join(files_and_dirs)
            self.terminal_text.insert(tk.END, f"{output}\n\n")
            self.terminal_text.see(tk.END)  # Auto-scroll to the end
        except Exception as e:
            self.terminal_text.insert(tk.END, f"Error listing directory: {e}\n\n")

    def change_directory(self, command):
        """Change the current working directory."""
        path = command.split(maxsplit=1)[1]
        try:
            os.chdir(path)
            self.terminal_text.insert(tk.END, f"Changed directory to: {os.getcwd()}\n\n")
        except FileNotFoundError:
            self.terminal_text.insert(tk.END, f"Directory not found: {path}\n\n")

    def start_adb_shell(self):
        """Start ADB shell in a new terminal window."""
        if platform.system() == "Windows":
            os.system("start cmd /k adb shell")
        elif platform.system() == "Darwin":
            os.system("open -a Terminal adb shell")
        else:
            os.system("x-terminal-emulator -e 'adb shell'")

    def run_command_with_realtime_output(self, command):
        """Run a shell command and stream its output in real-time."""
        try:
            # Start the process
            self.current_process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
                universal_newlines=True
            )

            # Read output in real-time
            while True:
                output = self.current_process.stdout.readline()
                if output == "" and self.current_process.poll() is not None:
                    break
                if output:
                    # Update the terminal text widget in the main thread
                    self.master.after(0, self.terminal_text.insert, tk.END, output)
                    self.master.after(0, self.terminal_text.see, tk.END)  # Auto-scroll
                    #time.sleep(0.05)  # Update interval (0.05 seconds)

            # Capture any remaining output
            remaining_output, _ = self.current_process.communicate()
            if remaining_output:
                self.master.after(0, self.terminal_text.insert, tk.END, remaining_output)
                self.master.after(0, self.terminal_text.see, tk.END)  # Auto-scroll

            # Add a newline after the command finishes
            self.master.after(0, self.terminal_text.insert, tk.END, "\n")

        except FileNotFoundError:
            self.master.after(0, self.terminal_text.insert, tk.END, f"Command not found: {command}\n\n")
        finally:
            self.current_process = None  # Reset the process handle

    def send_ctrl_c(self):
        """Send a CTRL+C signal to the currently running process."""
        if self.current_process:
            try:
                # Send SIGINT (CTRL+C) to the process
                if platform.system() == "Windows":
                    self.current_process.terminate()  # Windows doesn't support SIGINT
                else:
                    self.current_process.send_signal(signal.SIGINT)
                self.terminal_text.insert(tk.END, "\nCommand terminated with CTRL+C.\n")
            except Exception as e:
                self.terminal_text.insert(tk.END, f"\nError terminating command: {e}\n")
        else:
            self.terminal_text.insert(tk.END, "\nNo command is currently running.\n")

    def navigate_history(self, event):
        """Navigate through command history using up/down arrows."""
        if event.keysym == "Up":
            if self.command_index > 0:
                self.command_index -= 1
        elif event.keysym == "Down":
            if self.command_index < len(self.command_history) - 1:
                self.command_index += 1
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, self.command_history[self.command_index])

    def clear_terminal(self):
        """Clear the terminal text widget."""
        self.terminal_text.delete("1.0", tk.END)
        
    def copy_selected_text(self, event=None):
        """Copy selected text to the clipboard when left-clicking."""
        try:
            selected_text = self.terminal_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.update()  # Update clipboard
        except tk.TclError:
            pass  # No text selected
        