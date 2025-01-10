import sys

sys.path.append(".")
sys.path.append("src")

from src.utils import load_data, initialize_interface

# Main program
if __name__ == "__main__":
    data = load_data()
    initialize_interface(data)  # This will handle the UI interaction loop