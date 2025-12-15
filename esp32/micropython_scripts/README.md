# ESP32 Project

This project contains all tools, scripts, and firmware necessary to work with an ESP32 microcontroller using a Conda-based Python development environment.

---

## 🧰 Project Structure

```
esp32-project/
├── environment.yml            # Conda environment specification
├── firmware/                  # Precompiled firmware (.bin files)
│   └── micropython.bin
├── scripts/                   # Flashing and utility scripts
│   └── flash.py
├── src/                       # Your MicroPython or host-side Python code
│   └── main.py
└── README.md                  # Project documentation
```

---

## 📦 Setup Instructions

### 1. 🔧 Create the Conda environment locally

```bash
conda env create --prefix ~/esp32-envs/esp32-dev -f environment.yml
conda activate ~/esp32-envs/esp32-dev
```

*Note:* Keep the environment on your local machine for performance and reliability.

### 2. 🔌 Connect your ESP32

Find your serial port using:

```bash
ls /dev/tty.* | grep usb
```

Update `flash.py` with the correct port or pass it using `--port`.

---

## 🚀 Flashing & Erasing Firmware

From the project root:

### Erase flash only
```bash
python scripts/flash.py --erase-only --port /dev/cu.usbserial-0001
```

### Flash firmware
```bash
python scripts/flash.py firmware/micropython.bin
```

Optional flags:
```bash
--port /dev/cu.usbserial-0001
--baud 115200
--offset 0x1000
```

Example:

```bash
python scripts/flash.py firmware/micropython.bin --port /dev/cu.usbserial-0001 --baud 460800
```

---

## 🧠 Tips

- To update the environment file after installing packages:

  ```bash
  conda env export --from-history > environment.yml
  ```

- To run code from inside Vim:

  ```vim
  :!python %
  ```

- To test your ESP32 or read its flash ID:

  ```bash
  esptool -p /dev/cu.usbserial-0001 flash_id
  ```

---

## 🧼 Cleanup

To deactivate or remove the local environment:

```bash
conda deactivate
conda remove --prefix ~/esp32-envs/esp32-dev --all
```

---

## 📄 License

MIT License or your choice.

---

## 🖥️ Serial Monitor

To open a serial connection to the ESP32 (e.g., to use MicroPython REPL), use:

```bash
screen /dev/cu.usbserial-0001 115200
```

- Use `Control-A` then `Control-\` to exit `screen`.
- Make sure no other program is using the port (e.g., Thonny, Arduino, etc.)
