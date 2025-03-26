# main.py
import tkinter as tk
from tkinter import ttk
from adb_manager import FileManagerPage, APKManagerPage, NetworkManagerPage, ToolsPage, TerminalPage
from PIL import Image, ImageTk  # For loading PNG icons
import os
  x
class ADBApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ADB Manager")
        #self.geometry("800x600")  # Set a default window size
        style = ttk.Style()
        style.theme_use("clam")

        # Load PNG icons for tabs
        self.icons = {
            "file_manager": self.load_icon("file_manager.png", 30, 30),
            "apk_manager": self.load_icon("apk_manager.png", 30, 30),
            "network_manager": self.load_icon("network_manager.png", 30, 30),
            "tools": self.load_icon("tools.png", 30, 30),
            "terminal": self.load_icon("terminal.png", 30, 30),
        }

        # Create a notebook (tabbed interface)
        self.pages = ttk.Notebook(self)
        self.pages.pack(fill=tk.BOTH, expand=True)

        # Initialize all pages
        self.file_manager_page = FileManagerPage(self.pages)
        self.apk_manager_page = APKManagerPage(self.pages)
        self.network_manager_page = NetworkManagerPage(self.pages)
        self.tools_page = ToolsPage(self.pages)
        self.terminal_page = TerminalPage(self.pages)

        # Add pages to the notebook with icons and labels
        self.pages.add(self.file_manager_page, text="File Manager", image=self.icons["file_manager"], compound=tk.LEFT)
        self.pages.add(self.apk_manager_page, text="APK Manager", image=self.icons["apk_manager"], compound=tk.LEFT)
        self.pages.add(self.network_manager_page, text="Network Manager", image=self.icons["network_manager"], compound=tk.LEFT)
        self.pages.add(self.tools_page, text="Tools", image=self.icons["tools"], compound=tk.LEFT)
        self.pages.add(self.terminal_page, text="Terminal", image=self.icons["terminal"], compound=tk.LEFT)

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

if __name__ == "__main__":
    app = ADBApp()
    app.mainloop()
