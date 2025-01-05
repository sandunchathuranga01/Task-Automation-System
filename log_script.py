import logging
import datetime
import os
import zipfile
from logging.handlers import RotatingFileHandler
from threading import Timer

from Configuration.FilePath import Zipped_log_files, log_file_path


class PartRotatingFileHandler(RotatingFileHandler):
    def __init__(self, base_filename, maxBytes, backupCount=0, encoding=None, delay=False):
        self.part_num = 1
        self.base_filename = base_filename
        filename = self._get_next_filename()
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)

    def _get_next_filename(self):
        filename = self.base_filename.replace("01", f"{str(self.part_num).zfill(2)}")
        self.part_num += 1
        return filename

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        self.baseFilename = self._get_next_filename()

        if not self.delay:
            self.stream = self._open()

        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
                if os.path.exists(sfn):
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)


def zip_and_move_log_folder():
    """Function to zip the entire day's log folder and move it to the Previous_log directory at 23:59:59."""
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')

    # Define the directory path for the current day's logs
    log_folder_path = os.path.join(Live_log_directory)

    # Create the zip file name
    zip_filename = os.path.join(Previous_log_directory, f"{year}-{month}-{day}")

    # Check if the log folder exists and zip it
    if os.path.exists(log_folder_path):
        # Close all handlers to release file locks
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(log_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=Live_log_directory)  # Preserve folder structure
                    zipf.write(file_path, arcname)

        # Remove the original log folder after zipping
        for root, dirs, files in os.walk(log_folder_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

        print(f"Zipped and moved log folder: {log_folder_path} to {zip_filename}")
        logger.info((f"Zipped and moved log folder: {log_folder_path} to {zip_filename}"))
    else:
        print(f"Log folder does not exist: {log_folder_path}")
        logger.error(f"Log folder does not exist: {log_folder_path}")


def schedule_end_of_day_zip():
    """Schedule the zipping operation to run at 23:59:59."""
    now = datetime.datetime.now()
    # Set target time to 23:59:59 of the current day
    target_time = now.replace(hour=23, minute=59, second=59, microsecond=59)
    if now >= target_time:
        # If the current time is already past the target time, set the target to the next day
        target_time = target_time + datetime.timedelta(days=1)
    seconds_until_target_time = (target_time - now).total_seconds()
    Timer(seconds_until_target_time, zip_and_move_log_folder).start()


# Load the Configuration/FilePathLocations.json file
config_file_path = "Configuration/FilePathLocations.json"

log_file_location = log_file_path

if not log_file_location:
    raise ValueError("logFileLocation not found in the configuration file")

# Get the current date in the desired format
now = datetime.datetime.now()
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')

# Define the directory structure: logFileLocation/year-month-day
Live_log_directory = os.path.join(log_file_location, "VMS_LOG", "Live_log", f"{year}-{month}-{day}")
Previous_log_directory = os.path.join(log_file_location, "VMS_LOG", "Previous_log")

# Ensure the directory structure exists
try:
    os.makedirs(Live_log_directory, exist_ok=True)
except OSError as e:
    print(f"Error creating log directory: {e}")
    raise

try:
    os.makedirs(Previous_log_directory, exist_ok=True)
except OSError as e:
    print(f"Error creating log directory: {e}")
    raise

# Create a custom log filename with the directory, date, and '_VMS.log'
base_log_filename = os.path.join(Live_log_directory, f"01 -- {day}-{month}-{year} -- VMS Task Automation System")


# Create a PartRotatingFileHandler that creates a new log file when the size exceeds 512MB
max_log_size = 15 * 1024  # 15MB
handler = PartRotatingFileHandler(base_log_filename, maxBytes=max_log_size)

# Create a logger if it doesn't already exist
logger = logging.getLogger("VMSLogger")
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)

    # Set the format for the logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

# Schedule the log folder zipping at the end of the day
schedule_end_of_day_zip()
