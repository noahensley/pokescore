# Define variables
PYINSTALLER = pyinstaller
SCRIPT = ../src/main.py
OUTPUT_DIR = ../dist
TEMP_DIR = temp
UTILS_DIR = $(PWD)/../utils

# Default target
all: build

# Build the executable
build:
	@echo "Building executable with PyInstaller..."
	@mkdir -p $(TEMP_DIR)
	$(PYINSTALLER) --onefile --add-data "$(UTILS_DIR):utils" $(SCRIPT) --specpath $(TEMP_DIR) --workpath $(TEMP_DIR) --distpath $(OUTPUT_DIR)
	@if [ -d $(TEMP_DIR) ]; then rm -rf $(TEMP_DIR); fi
	@if [ -d $(OUTPUT_DIR) ]; then \
		echo "Build completed successfully. Check the $(OUTPUT_DIR) directory for the executable."; \
	else \
		echo "Build failed. Please check for errors."; \
		exit 1; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(OUTPUT_DIR)
	@rm -rf $(TEMP_DIR)
	@rm -rf build/
	@rm -f *.spec
	@echo "Clean completed."

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r ../requirements.txt

# Install PyInstaller if not present
install-pyinstaller:
	@echo "Installing PyInstaller..."
	pip install pyinstaller

# Full setup: install dependencies and build
setup: install build

# Help target
help:
	@echo "Available targets:"
	@echo "  build              - Build the executable"
	@echo "  clean              - Clean build artifacts"
	@echo "  install            - Install dependencies from requirements.txt"
	@echo "  install-pyinstaller - Install PyInstaller"
	@echo "  setup              - Install dependencies and build"
	@echo "  help               - Show this help message"

.PHONY: all build clean install install-pyinstaller setup help