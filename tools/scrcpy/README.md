# scrcpy-windows-exec

This repository provides an easy way to use [`scrcpy`](https://github.com/Genymobile/scrcpy/releases) on **Windows** without needing to install or build it from source.

If you're on **Windows**, you can use the precompiled executable available from the official releases.

## 📱 What is scrcpy?

`scrcpy` is a free and open-source application that allows you to mirror and control Android devices from your computer via USB or over TCP/IP.

## ✅ Features

- High performance screen mirroring
- Control Android device with mouse and keyboard
- No root required
- Works via USB and wireless (TCP/IP)
- Lightweight and easy to use

## 🖥️ Usage on Windows

### Option 1: Download and Use

1. **Download the latest release** of scrcpy from the official page:  
   👉 [https://github.com/Genymobile/scrcpy/releases](https://github.com/Genymobile/scrcpy/releases)

2. **Extract the ZIP file**.

3. **Copy the following files** from the extracted folder into this project directory (next to this `README.md`):
   - `scrcpy.exe`
   - `adb.exe`
   - `AdbWinApi.dll`
   - `AdbWinUsbApi.dll`

   > These are needed for `scrcpy` to run correctly on Windows.

4. **Connect your Android device via USB** and enable **USB debugging**.


## 🔧 Requirements

- Windows 7 or higher
- Android device with USB debugging enabled
- [ADB](https://developer.android.com/studio/command-line/adb) (included in the ZIP)

## 📡 Wireless Usage (Optional)

1. Connect the device via USB.
2. Enable TCP/IP mode:
    ```bash
    adb tcpip 5555
    ```
3. Disconnect USB and connect via IP:
    ```bash
    adb connect DEVICE_IP:5555
    scrcpy.exe
    ```

## 📝 License

scrcpy is developed by [Genymobile](https://github.com/Genymobile) and licensed under the Apache License 2.0.

---

