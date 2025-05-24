import logging
from utils.adb_utils import ADBUtils
from attack_sequence.attack_sequence import AttackSequence
from search_sequence.search_sequence import SearchSequence
from starting_sequence.starting_sequence import StartingSequence

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def list_devices() -> list[str]:
    """Return list of connected ADB device serial numbers."""
    import os
    lines = os.popen("adb devices").read().strip().splitlines()
    devices = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices

def prompt_device_selection(devices: list[str]) -> list[str]:
    print("Connected devices:")
    for idx, dev in enumerate(devices, 1):
        print(f"  {idx}. {dev}")
    choice = input("Enter device numbers (comma-separated) or 'all': ")
    if choice.strip().lower() == 'all':
        return devices
    selected = []
    for part in choice.split(','):
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= len(devices):
                selected.append(devices[idx - 1])
    return selected

def main():
    devices = list_devices()
    if not devices:
        logging.error("No connected devices found. Ensure ADB is running.")
        return

    selected = prompt_device_selection(devices)
    if not selected:
        logging.error("No valid devices selected. Exiting.")
        return

    logging.info(f"Selected devices: {selected}")
    print("\n[SAFETY] This tool is for educational purposes. Confirm to continue.")
    confirm = input("Type 'yes' to continue: ")
    if confirm.strip().lower() != 'yes':
        print("Aborted by user.")
        return

    for serial in selected:
        print(f"[INFO] Running sequences for device: {serial}")
        # Run starting sequence
        start_seq = StartingSequence(serial)
        start_seq.run()
        # Run search sequence
        search_seq = SearchSequence(serial)
        search_seq.run()
        # Run attack sequence
        attack_seq = AttackSequence(serial)
        attack_seq.run()

if __name__ == '__main__':
    main()
