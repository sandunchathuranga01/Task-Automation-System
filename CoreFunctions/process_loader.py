import json
import threading
from datetime import datetime, timedelta
from log_script import logger  # Import logger for logging messages
from Configuration.FilePath import Process_json_file_path  # Import process JSON file path
from CoreFunctions.ProcessRefreshTimer import refresh_interval  # Import refresh interval

# Initialize the array lists
lookingProcess = []  # List of processes that are currently active and not marked for removal
Processes = []  # List of all processes currently being monitored

# Function to load processes from a JSON file
def load_processes_from_json(file_path):
    global lookingProcess  # Declare global to modify the global list
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data from file
            all_processes = data.get("root", {}).get("VMSProcess", [])  # Get list of all processes
            # Filter processes that are active and not marked for removal
            lookingProcess = [process for process in all_processes if process.get("Sequence") != "99" and process.get("ProcessSwitch") == "ON"]
            print(f"Successfully loaded processes from {file_path}")
            logger.info(f"Successfully loaded processes from {file_path}")
            print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        logger.error(f"Error: File {file_path} not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
        logger.error("Error: Failed to decode JSON from the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")

# Function to update the current processes list based on the loaded processes
def update_processes():
    global Processes  # Declare global to modify the global list
    try:
        current_processes_dict = {process['ProcessName']: process for process in Processes}  # Create a dictionary of current processes
        looking_process_names = {process['ProcessName'] for process in lookingProcess}  # Set of process names currently active

        # Add new or updated processes
        for process in lookingProcess:
            if process['ProcessName'] not in current_processes_dict:
                Processes.append(process)
                print(f"Added new process: {process['ProcessName']}")
                logger.info(f"Added new process: {process['ProcessName']}")
            elif current_processes_dict[process['ProcessName']] != process:
                index = Processes.index(current_processes_dict[process['ProcessName']])
                Processes[index] = process
                print(f"Updated process: {process['ProcessName']}")
                logger.info(f"Updated process: {process['ProcessName']}")

        # Remove processes that are no longer active
        Processes = [process for process in Processes if process['ProcessName'] in looking_process_names]
        for process_name in current_processes_dict:
            if process_name not in looking_process_names:
                print(f"Removed process: {process_name}")
                logger.info(f"Removed process: {process_name}")

    except Exception as e:
        print(f"An error occurred while updating processes: {e}")
        logger.error(f"An error occurred while updating processes: {e}")

# Function to refresh the list of active processes periodically
def refresh_looking_process():
    try:
        load_processes_from_json(Process_json_file_path)  # Reload the processes from the JSON file
        update_processes()  # Update the current list of processes
        next_refresh_time = datetime.now() + timedelta(seconds=refresh_interval)  # Calculate next refresh time

        # print("Looking Process List:\n", json.dumps(lookingProcess, indent=2))  #veiw Looking process
        # print("Processes List:\n", json.dumps(Processes, indent=2))  #view Process List
        # print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
        # print(f"System refresh interval: {refresh_interval} seconds")
        logger.info(f"System refresh interval: {refresh_interval} seconds")
        logger.info(f"Next refresh time: {next_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
        threading.Timer(refresh_interval, refresh_looking_process).start()  # Schedule the next refresh
    except Exception as e:
        print(f"An error occurred while refreshing processes: {e}")
        logger.error(f"An error occurred while refreshing processes: {e}")
