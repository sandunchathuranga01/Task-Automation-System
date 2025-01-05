import logging
import datetime
import os
from logging.handlers import RotatingFileHandler

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


# Load the Configuration/FilePathLocations.json file
config_file_path = "../Configuration/FilePathLocations.json"

log_file_location = log_file_path

if not log_file_location:
    raise ValueError("logFileLocation not found in the configuration file")

# Get the current date in the desired format
now = datetime.datetime.now()
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')

# Define the directory structure: logFileLocation/year-month-day
Live_log_directory = os.path.join(log_file_location, "VMS_LOG","Live_log", f"{year}-{month}-{day}")

Previous_log_directory = os.path.join(log_file_location, "VMS_LOG","Previous_log")

# Ensure the directory structure exists
try:
    os.makedirs(Live_log_directory, exist_ok=True)
except OSError as e:
    print(f"Error creating log directory: {e}")
    raise

# Ensure the directory structure exists
try:
    os.makedirs(Previous_log_directory, exist_ok=True)
except OSError as e:
    print(f"Error creating log directory: {e}")
    raise

# Create a custom log filename with the directory, date, and '_VMS.log'
base_log_filename = os.path.join(Live_log_directory, f"01 -- {day}-{month}-{year} -- DAY VMS logger")

# Create a PartRotatingFileHandler that creates a new log file when the size exceeds 512MB
max_log_size = 15 * 1024  # 15MB
handler = PartRotatingFileHandler(base_log_filename, maxBytes=max_log_size)

# Create a logger if it doesn't already exist
logger = logging.getLogger("VMSLogger")
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)

    # Set the format for the logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)


