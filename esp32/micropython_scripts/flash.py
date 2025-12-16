import os
import subprocess
import sys
import argparse
from datetime import datetime

# --- Argument parser ---
parser = argparse.ArgumentParser(description="Flash firmware to ESP32 using esptool.")
parser.add_argument("firmware", nargs="?", help="Path to the .bin firmware file to flash")
parser.add_argument("--port", default="/dev/cu.usbserial-0001",
                    help="Serial port for ESP32 (default: /dev/cu.usbserial-0001)")
parser.add_argument("--baud", default="460800",
                    help="Baud rate (default: 460800)")
parser.add_argument("--offset", default="0x1000",
                    help="Flash offset address (default: 0x1000)")
parser.add_argument("--erase-only", action="store_true",
                    help="Only erase the flash and exit")

args = parser.parse_args()

# --- Helper function ---
def run_command(cmd):
    print(f"[{datetime.now()}]: \n>>> Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[{datetime.now()}]: ✅ Success")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}]: ❌ Error:", e)
        sys.exit(1)

# --- Flashing steps ---
if __name__ == "__main__":
    if not args.erase_only:
        if not args.firmware:
            print(f"[{datetime.now()}]: ❌ No firmware specified. Provide a .bin file or use --erase-only.")
            sys.exit(1)
        if not os.path.exists(args.firmware):
            print(f"[{datetime.now()}]: ❌ Firmware not found: {args.firmware}")
            sys.exit(1)

    print(f"[{datetime.now()}]: 🔌 Flashing ESP32 on port {args.port}...")

    # Step 1: Erase flash
    run_command(["esptool", "-p", args.port, "erase-flash"])

    # Stop here if erase-only
    if args.erase_only:
        print(f"[{datetime.now()}]: 🧹 Flash erase completed. Exiting (--erase-only).")
        sys.exit(0)

    # Step 2: Write firmware
    run_command([
        "esptool", "-p", args.port, "-b", args.baud,
        "write-flash", "-z", args.offset, args.firmware
    ])
