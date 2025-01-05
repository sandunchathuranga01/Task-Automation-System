import os
from log_script import logger  # Import the logger from log_script.py

# Check the operating system
def print_os_name():
    # Check if the operating system is Windows
    if os.name == 'nt':
        logger.info("Operating System: Windows")  # Log the OS name as Windows
        print("Operating System: Windows")  # Print the OS name as Windows to the console
    # Check if the operating system is Unix-like (Linux, macOS, etc.)
    elif os.name == 'posix':
        logger.info("Operating System: Unix-like (Linux, macOS, etc.)")  # Log the OS name as Unix-like
        print("Operating System: Unix-like (Linux, macOS, etc.)")  # Print the OS name as Unix-like to the console
    # Handle unknown operating systems
    else:
        logger.warning("Operating System: Unknown")  # Log the OS name as unknown
        print("Operating System: Unknown")  # Print the OS name as unknown to the console

