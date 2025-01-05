import json
import os
from threading import Event  # Import Event for managing thread signals
from log_script import logger  # Import logger for logging messages

from Configuration.FilePath import system_switch_file_path  # Import file path for system switch
from CoreFunctions.scheduler import stop_all_processes  # Import function to stop all processes

# Event to signal shutdown
shutdown_event = Event()  # Create an Event object to signal shutdown

# Function to check the current system status from a JSON configuration file
def check_system_status():
    try:
        print("Checking system status...")
        logger.info("Checking system status...")
        with open(system_switch_file_path, 'r') as file:
            data = json.load(file)  # Load JSON data from file

        if 'root' in data and 'SystemStatus' in data['root']:
            system_status_key = data['root']['SystemStatus'].get('SystemStatusKey')  # Get system status key
            if system_status_key == "ON":
                print("System status is ON. The system will run.")
                logger.info("System status is ON. The system will run.")
                return True
            elif system_status_key == "OFF":
                print("System status is OFF. The system will not run.")
                logger.info("System status is OFF. The system will not run.")
                return False
            else:
                print("Unknown SystemStatusKey value. The system will not run.")
                logger.warning("Unknown SystemStatusKey value. The system will not run.")
                return False
        else:
            print("Missing or incorrect keys in JSON. The system will not run.")
            logger.warning("Missing or incorrect keys in JSON. The system will not run.")
            return False
    except FileNotFoundError:
        print("SystemSwitch.json file is missing. The system will not run.")
        logger.error("SystemSwitch.json file is missing. The system will not run.")
        return False
    except json.JSONDecodeError:
        print("Error decoding JSON (possibly malformed). The system will not run.")
        logger.error("Error decoding JSON (possibly malformed). The system will not run.")
        return False

# Function to initiate a system shutdown
def shutdown():
    print("Initiating shutdown...")
    logger.info("Initiating shutdown...")
    stop_all_processes()  # Call stop_all_processes() function to stop all running processes
    print("All processes have been stopped.")
    logger.info("All processes have been stopped.")
    os._exit(0)  # Forcefully exit the program
