import json
from log_script import logger  # Import logger for logging messages

# Global variable for the refresh interval (in seconds)
refresh_interval = 600  # Default refresh interval set to 600 seconds (10 minutes)

# Dictionary to store the last firing time of each process
last_firing_time = {}  # Store the last time each process was executed

# Function to load system refresh timer from JSON file and update refresh interval
def ProcessRefreshTimer(file_path):
    global refresh_interval  # Declare global to modify the global variable
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data from file
            timer_str = data.get("TaskSystem", {}).get("systemRefreshTimer", "00:00:30")  # Get the refresh timer string
            new_refresh_interval = parse_frequency_to_seconds(timer_str)  # Parse the timer string into seconds
            # Update the refresh interval if it has changed
            if new_refresh_interval != refresh_interval:
                refresh_interval = new_refresh_interval
                print(f"Updated system refresh interval: {refresh_interval} seconds")
                logger.info(f"Updated system refresh interval: {refresh_interval} seconds")

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        logger.error(f"Error: File {file_path} not found.")

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
        logger.error("Error: Failed to decode JSON from the file.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")

# Function to parse a frequency string (HH:MM:SS) into total seconds
def parse_frequency_to_seconds(frequency):
    try:
        h, m, s = map(int, frequency.split(':'))  # Split and convert time components to integers
        return h * 3600 + m * 60 + s  # Calculate total seconds
    except Exception as e:
        print(f"An error occurred while parsing frequency to seconds: {e}")
        logger.error(f"An error occurred while parsing frequency to seconds: {e}")
        return 0
