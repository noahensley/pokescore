import sys

sys.path.append(".")
sys.path.append("src")

import UIInfo

# Main program
if __name__ == "__main__":
    try:
        print("Starting Pokescore Application...")
        ui = UIInfo.UIInfo()
    except RuntimeError as e:
        print(f"ERROR: {e}\nExiting...")
        exit()