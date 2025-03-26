# ADB Manager - Comprehensive Android Debug Bridge Tool

ADB Manager is a **Graphical User Interface (GUI) tool** built with **Python** and **Tkinter**, designed to simplify **Android Debug Bridge (ADB)** operations.  
It provides an intuitive interface for **file management, APK handling, network controls, device tools, and ADB shell commands**.

<p align="center">
  <img src="screenshots/file_manager.png" width="700" alt="Main Interface">
</p>

---

## 📌 **Features**

### 📂 **File Management**
- Browse the device file system with **icon-based visualization**.
- Upload/download files and folders.
- Create/delete directories.
- Copy/Paste operations.
- **Compress/Decompress files** (`tar.gz` format).
- Toggle hidden file visibility.

### 📦 **APK Management**
- **List all installed apps** with icons.
- Install/uninstall APKs.
- Enable/disable applications.
- **Extract APKs** from the device.
- Clear app data.
- Launch applications.
- View **detailed package information**.

### 🛠 **Device Tools**
- Take **screenshots** and save them automatically.
- Record the device screen.
- View **detailed device information**.
- Control **volume and power settings**.
- **Reboot device** (normal, recovery, bootloader).
- **Scrcpy integration** for screen mirroring.
- Start/Stop **ADB service**.

### 🌐 **Network Controls**
- Enable/disable **WiFi, Bluetooth, Airplane Mode, and Mobile Data**.
- Connect ADB **over TCP/IP**.
- Detect device IP addresses.

### 💻 **Terminal**
- Full ADB shell access with **real-time output**.
- Command history navigation (**Up/Down arrows**).
- Process control (`CTRL+C` support).
- Directory navigation shortcuts.

---

## 🛠 **Installation Guide**

### **1. Prerequisites**
Ensure the following are installed on your system:
- **Python 3.7 or higher** – [Download here](https://www.python.org/downloads/)
- **ADB (Android Debug Bridge)** – Installed and added to the system `PATH`
- **Android device** with **USB Debugging enabled**

### **2. Clone the Repository**
```bash
git clone https://github.com/Electro-Gamma/adb-manager.git
cd adb-manager
```

### **3. Install Required Python Packages**

This tool is **cross-platform** and works on:
- **Windows (10/11)**
- **Linux (Most distributions)**
- **macOS (10.15+)**

Install dependencies with:
```bash
pip install -r requirements.txt
```

### **Platform-Specific Notes**
| Platform  | Additional Notes |
|-----------|-----------------|
| **Windows** | ✅ No extra requirements – works out of the box |
| **Linux**  | 🔧 Run: `sudo apt-get install python3-tk` (for Debian/Ubuntu) |
| **macOS**  | 🍎 Run: `brew install python-tk` (via Homebrew) |

💡 **Troubleshooting**
- On **Linux/macOS**, use `pip3` if `pip` doesn't work.
- Add `--user` flag if getting **permission errors**:
  ```bash
  pip install --user -r requirements.txt
  ```
- For **ARM devices** (Raspberry Pi / Apple M1/M2 Macs), use:
  ```bash
  pip install --prefer-binary pillow
  ```


### **4. (Optional) Add Custom Icons**
- Place `.png` icon files inside the `icons/` directory.
- Ensure they match names in `icon_mappings.json`.

### **5. Run ADB Manager**
```bash
python app.py
```

---

## 🔌 **How to Connect Your Android Device**

1. **Enable USB Debugging on Your Android Device**  
   - Go to **Settings → About Phone → Tap "Build Number" 7 times** to enable **Developer Options**.
   - Navigate to **Developer Options → Enable "USB Debugging"**.

2. **Connect Your Device via USB**
   - Plug in your device to the computer via **USB cable**.
   - Run:
     ```bash
     adb devices
     ```
   - If prompted on your device, **allow debugging**.

3. **Run ADB Manager**
   ```bash
   python app.py
   ```
   - If the connection is successful, your device will be listed.

---

## 🎯 **Usage Guide**

### **1. Basic File Operations**
- **Double-click folders** to navigate.
- **Ctrl+Click or Shift+Click** to select multiple files/folders.
- Drag-and-drop file support (if implemented).

### **2. Take Screenshots**
- Screenshots are saved automatically in:
  ```
  device-pull/[device-model]/screenshot/
  ```

### **3. Record Screen**
- Screen recordings are saved in:
  ```
  device-pull/[device-model]/screenrecord/
  ```

### **4. Connect ADB Over WiFi**
1. Connect device via **USB** first.
2. Use **Network Manager** to get the device IP.
3. Click **"Connect"** to enable **ADB over TCP/IP**.
4. Disconnect USB, and **continue managing via WiFi**.

---

## ⚙ **Configuration Options**

### **Configuration Files**
- `icon_mappings.json` → Maps file extensions to icons.

### **Environment Variables**
- `ADB_PATH` → Override the default ADB executable path.
- `DEFAULT_SAVE_PATH` → Change the default download location.

---

## 🚑 **Troubleshooting & Common Issues**

### ❓ **Device Not Detected**
**Solution:**
- Ensure **USB Debugging** is enabled.
- Run:
  ```bash
  adb devices
  ```
  If no device appears, try:
  ```bash
  adb kill-server
  adb start-server
  ```
- Try a **different USB cable/port**.

### ❓ **Permission Denied Errors**
**Solution:**
- If prompted on your device, **allow USB Debugging**.
- Try:
  ```bash
  adb shell
  ```

### ❓ **ADB Over WiFi Not Connecting**
**Solution:**
1. Ensure the device and PC are **on the same WiFi network**.
2. Restart **ADB over TCP/IP**:
   ```bash
   adb tcpip 5555
   adb connect <device-ip>:5555
   ```

### ❓ **Icons Not Displaying Correctly**
**Solution:**
- Ensure **PNG files exist** in `icons/` directory.
- Check **`icon_mappings.json`** for correct mappings.

---

## 📜 **License**
This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🙌 **Acknowledgments**
- **[ADB](https://developer.android.com/studio/command-line/adb)** – Android Debug Bridge.  
- **[Scrcpy](https://github.com/Genymobile/scrcpy)** – Screen mirroring.  
- **[Pillow](https://python-pillow.org/)** – Image processing.  
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** – GUI framework.  

---

## 📧 **Contact & Support**
For questions or feedback, feel free to reach out:

📧 **Email**: your.email@example.com  
🐙 **GitHub**: [Electro-Gamma](https://github.com/Electro-Gamma)

---

## 📷 **Screenshots Folder**
All **UI screenshots** should be placed inside the `images/` folder.

---

### 🎉 **Enjoy managing your Android devices with ADB Manager!**

