import json


# Load JSON data from FilePathLocations.json
def load_file_paths(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['paths']['file']
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} could not be decoded as JSON.")
        return []

# Extract file paths
def get_file_path(location_name, file_paths):
    for path in file_paths:
        if path['locationName'] == location_name:
            return path['location']
    print(f"Error: No path found for location name '{location_name}'.")
    return None

# Example usage with an absolute path
file_paths = load_file_paths('C:\\Users\\Chathuranga\\Desktop\\VB\\Configuration\\FilePathLocations.json')


system_switch_file_path = get_file_path('system_switch_file_path', file_paths)
log_file_path = get_file_path('logFileLocation', file_paths)
Zipped_log_files = get_file_path('Zipped_log_files', file_paths)
Process_json_file_path = get_file_path('Process_json_file_path', file_paths)
process_schedule_json_file_path = get_file_path('process_schedule_json_file_path', file_paths)
ProcessRefreshTimer_json_file_path = get_file_path('ProcessRefreshTimer_json_file_path', file_paths)




