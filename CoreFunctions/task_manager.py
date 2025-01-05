import os
import subprocess  # Import subprocess to execute shell commands
from datetime import datetime
from mysql.connector import Error  # Import MySQL connector Error class
from Shared_modules.DB_Config import create_db_connection  # Import function to create a DB connection
from log_script import logger  # Import logger for logging messages

# Function to query tasks related to a process and execute a command
def query_tasks_related_to_process(process):
    process_name = process['ProcessName']  # Get the process name
    process_script = process.get('process_scrip')  # Get the script to execute for the process

    # Determine the correct process location based on the OS
    if os.name == 'nt':  # Windows
        process_location = process.get('WINDOWS_process_location')
    elif os.name == 'posix':  # Unix-based systems (Linux, macOS)
        process_location = process.get('LINUX_process_location')
    else:
        print("Operating System: Unknown")
        logger.warning("Operating System: Unknown")
        return

    connection = create_db_connection()  # Create a database connection
    if connection:
        try:
            cursor = connection.cursor()  # Create a cursor to execute queries
            query = """
                SELECT TASK_ID, TASK_SCHEDULE_DTM 
                FROM TASK_HEADER 
                JOIN TEMPLATE_HEADER ON TASK_HEADER.HD_ID = TEMPLATE_HEADER.HD_ID 
                WHERE TEMPLATE_HEADER.TASK_NAME = %s AND TASK_HEADER.TASK_STATUS = 'END'
            """  # SQL query to fetch tasks related to the process
            cursor.execute(query, (process_name,))  # Execute the query with process name as parameter
            tasks = cursor.fetchall()  # Fetch all matching tasks
            if tasks:
                for task in tasks:
                    task_id = task[0]
                    task_schedule_dtm = task[1]
                    if task_schedule_dtm:
                        print(f"Task ID {task_id} is scheduled for {task_schedule_dtm}")
                        logger.info(f"Task ID {task_id} is scheduled for {task_schedule_dtm}")
                        if task_schedule_dtm > datetime.now():
                            print(f"Task ID {task_id} is scheduled to run at {task_schedule_dtm} and will not be executed now.")
                            logger.info(f"Task ID {task_id} is scheduled to run at {task_schedule_dtm} and will not be executed now.")
                            continue
                    print(f"TASK_ID: {task_id}")
                    logger.info(f"TASK_ID: {task_id}")
                    execute_process_command(connection, process, process_location, process_script, task_id)  # Execute the command for each task

            else:
                print(f"No open tasks found for process: {process_name}")
                logger.info(f"No open tasks found for process: {process_name}")
        except Error as e:
            print(f"Error while querying the database: {e}")
            logger.error(f"Error while querying the database: {e}")
        finally:
            cursor.close()
            connection.close()  # Close the database connection

# Function to execute the process command
def execute_process_command(connection, process, process_location, process_script, task_id):
    if process_script:
        try:
            parameters = {}  # Removed fetch_process_parameters call (empty for now)
            command = process_script.replace("<script_path>", f'"{process_location}"')  # Replace placeholders in script
            command = command.replace("<task_id>", str(task_id))  # Replace task ID placeholder
            for key, value in parameters.items():
                if ' ' in value:
                    value = f'"{value}"'
                placeholder = f"<{key}>"
                if placeholder in command:
                    command = command.replace(placeholder, value)
            print(f"Final command to execute: {command}")
            logger.info(f"Final command to execute: {command}")
            subprocess.run(command, check=True, shell=True)  # Execute the command using subprocess
            print(f"Command executed successfully for task ID {task_id}")
            logger.info(f"Command executed successfully for task ID {task_id}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the command for task ID {task_id}: {e}")
            logger.error(f"An error occurred while executing the command for task ID {task_id}: {e}")
        except Exception as e:
            print(f"An error occurred while preparing the command for task ID {task_id}: {e}")
            logger.error(f"An error occurred while preparing the command for task ID {task_id}: {e}")
