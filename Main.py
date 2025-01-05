import os
import time
from CoreFunctions.ProcessRefreshTimer import refresh_interval, ProcessRefreshTimer
from CoreFunctions.SystemSwitch import check_system_status, shutdown_event, shutdown
from CoreFunctions.OS_detection import print_os_name
from CoreFunctions.process_loader import refresh_looking_process
from CoreFunctions.scheduler import check_system_refresh_timer, start_firing_processes
from Configuration.FilePath import ProcessRefreshTimer_json_file_path

# Assuming logging is set up in log_script.py and logger is named "VMSLogger"
from logging import getLogger

logger = getLogger("VMSLogger")

def System():
    # ProcessRefreshTimer
    try:
        ProcessRefreshTimer(ProcessRefreshTimer_json_file_path)
        logger.info(f"Initial system refresh interval: {refresh_interval} seconds")
        print(f"Initial system refresh interval: {refresh_interval} seconds")
    except Exception as e:
        logger.error(f"An error occurred while loading the initial system refresh timer interval: {e}")

    # Start the periodic refresh and timer check
    try:
        refresh_looking_process()
        check_system_refresh_timer()
        logger.info("Periodic refresh and timer check started successfully.")
    except Exception as e:
        logger.error(f"An error occurred while starting the firing of all processes: {e}")

    # Start firing all processes
    try:
        start_firing_processes()
        logger.info("Firing of all processes started successfully.")
    except Exception as e:
        print(f"An error occurred while starting the firing of all processes: {e}")

def main():
    print_os_name()
    try:
        while True:
            if check_system_status():
                logger.info("System is running...")
                print("Running the system...")
                System()
            else:
                logger.warning("Exiting the program due to system status being OFF or an issue with the file.")
                print("Exiting the program due to system status being OFF or an issue with the file.")
                shutdown_event.set()  # Signal shutdown
                shutdown()
                os._exit(0)  # Forcefully exit the program

            logger.info("Waiting for 2 minutes before the next check...")
            print("Waiting for 2 minutes before the next check...")
            time.sleep(20)  # Waiting for 20 Second

    except KeyboardInterrupt:
        logger.info("Program interrupted manually. Shutting down gracefully...")
        print("Program interrupted manually. Shutting down gracefully...")
        shutdown_event.set()  # Signal shutdown
        shutdown()
        os._exit(0)  # Forcefully exit the program

if __name__ == "__main__":
    main()
