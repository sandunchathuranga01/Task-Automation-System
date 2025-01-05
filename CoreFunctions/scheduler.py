import json
import threading
from datetime import datetime, timedelta
from log_script import logger  # Import logger for logging messages
from Configuration.FilePath import process_schedule_json_file_path, ProcessRefreshTimer_json_file_path  # Import file paths
from CoreFunctions.ProcessRefreshTimer import parse_frequency_to_seconds, last_firing_time, ProcessRefreshTimer  # Import utility functions and variables
from CoreFunctions.process_loader import Processes  # Import list of processes
from CoreFunctions.task_manager import query_tasks_related_to_process  # Import task querying function

# List to hold all active timers
active_timers = []  # Store references to all running timers for process execution

# Function to check if a process should be fired based on its schedule
def should_fire_process(process):
    process_name = process['ProcessName']  # Get the process name
    current_time = datetime.now()  # Get the current time

    try:
        with open(process_schedule_json_file_path, 'r') as file:
            schedule_data = json.load(file)  # Load schedule data from JSON file
            all_schedules = schedule_data.get("root", {}).get("VMSProcess", [])  # Get all process schedules
            process_schedule = next((sched for sched in all_schedules if sched['ProcessName'] == process_name), None)  # Find the schedule for the current process
            if not process_schedule:
                print(f"No schedule found for process: {process_name}. Proceeding to run the process.")
                logger.info(f"No schedule found for process: {process_name}. Proceeding to run the process.")
                return True

            print(f"Checking schedule for process: {process_name}")
            logger.info(f"Checking schedule for process: {process_name}")
            current_day = current_time.strftime('%A')  # Get the current day of the week
            exclude_days = process_schedule.get("ProcessExcludeDay", [])  # Get list of excluded days for the process
            if exclude_days and current_day in exclude_days:
                print(f"Process {process_name} is excluded today ({current_day}).")
                logger.info(f"Process {process_name} is excluded today ({current_day}).")
                return False

            current_time_str = current_time.strftime('%H:%M')  # Get the current time as a string
            exclude_times = process_schedule.get("ProcessExcludeTime", [])  # Get list of excluded time ranges for the process
            for time_range in exclude_times:
                start_time, end_time = time_range.split('-')  # Split the time range into start and end times
                if start_time <= current_time_str <= end_time:
                    print(f"Process {process_name} is excluded at this time ({current_time_str}).")
                    logger.info(f"Process {process_name} is excluded at this time ({current_time_str}).")
                    return False

            specific_time = process_schedule.get("SpecificProcessTime")  # Get the specific time for the process to run
            if specific_time and current_time_str != specific_time:
                print(f"Process {process_name} is scheduled to run at {specific_time}, current time is {current_time_str}.")
                logger.info(f"Process {process_name} is scheduled to run at {specific_time}, current time is {current_time_str}.")
                return False

            return True

    except FileNotFoundError:
        print(f"Error: File {process_schedule_json_file_path} not found. Proceeding to run the process.")
        logger.error(f"Error: File {process_schedule_json_file_path} not found. Proceeding to run the process.")
        return True
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file. Proceeding to run the process.")
        logger.error("Error: Failed to decode JSON from the file. Proceeding to run the process.")
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")
        return True

# Function to fire processes based on their frequency
def fire_process(process):
    process_name = process['ProcessName']  # Get the process name
    frequency = process['ProcessFrequency']  # Get the frequency at which the process should be fired
    interval = parse_frequency_to_seconds(frequency)  # Parse the frequency into seconds

    # Inner function to handle the process firing logic
    def fire():
        try:
            if should_fire_process(process):
                current_time = datetime.now()  # Get the current time
                next_firing_time = current_time + timedelta(seconds=interval)  # Calculate the next firing time
                print(f"Firing process: {process_name} at {current_time.strftime('%Y-%m-%d %H:%M:%S')} | Next firing time: {next_firing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Firing process: {process_name} at {current_time.strftime('%Y-%m-%d %H:%M:%S')} | Next firing time: {next_firing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                last_firing_time[process_name] = current_time  # Update the last firing time for the process
                query_tasks_related_to_process(process)  # Query and execute tasks related to the process
                print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
            timer = threading.Timer(interval, fire)  # Schedule the next firing
            timer.start()
            active_timers.append(timer)  # Add timer to the list of active timers
        except Exception as e:
            print(f"An error occurred while firing process {process_name}: {e}")
            logger.error(f"An error occurred while firing process {process_name}: {e}")

    fire()

# Function to periodically check the system refresh timer
def check_system_refresh_timer():
    try:
        ProcessRefreshTimer(ProcessRefreshTimer_json_file_path)  # Update the system refresh timer based on configuration
        timer = threading.Timer(60, check_system_refresh_timer)  # Schedule the next check in 60 seconds
        timer.start()
        active_timers.append(timer)  # Add timer to the list of active timers
    except Exception as e:
        print(f"An error occurred while checking system refresh timer: {e}")
        logger.error(f"An error occurred while checking system refresh timer: {e}")

# Function to start firing all processes
def start_firing_processes():
    try:
        for process in Processes:
            process_name = process['ProcessName']  # Get the process name
            if process_name not in last_firing_time:
                last_firing_time[process_name] = datetime.now()  # Initialize the last firing time for the process
                fire_process(process)  # Start firing the process based on its schedule
    except Exception as e:
        print(f"An error occurred while starting the firing of processes: {e}")
        logger.error(f"An error occurred while starting the firing of processes: {e}")

# Function to stop all active timers
def stop_all_processes():
    print("Stopping all active processes...")
    logger.info("Stopping all active processes...")
    for timer in active_timers:
        timer.cancel()  # Cancel each active timer
