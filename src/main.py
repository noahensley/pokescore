import sys

sys.path.append(".")
sys.path.append("src")

import UIInfo

# Main program
if __name__ == "__main__":
    try:
        ui = UIInfo.UIInfo()
    except RuntimeError as e:
        print(f"ERROR: {e}\nExiting...")
        exit()