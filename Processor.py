import config.ConfigManager as ConfigManager
import os

SETUP_HEADER = "Scouter Name, Team Number, Match Number, Preloaded Fuel, Alliance Partner1, Alliance Partner2, Alliance Color, No Show"
EVENT_HEADER = "Scouter Name, Team Number, Match Number, A_coll,A_scor,A_miss,A_ferr,A_died,A_att,A_succ,A_loc,T_coll,T_scor,T_miss,T_ferr,T_died,E_att,E_succ,E_loc,timestamp"

# Strip comma from end if necessary
def strip_commas(full_str:str) -> str:
    if not full_str:
        return ""
    full_str = full_str.strip()
    while len(full_str) > 0 and full_str[-1] == ",":
        full_str = full_str[:-1]
    return full_str

# Get file paths from config
def get_paths():
    return ConfigManager.get_config().get('paths', {})

def initialize_files():
    paths = get_paths()
    for key, header in [('setup_list', SETUP_HEADER), ('event_list', EVENT_HEADER)]:
        path = paths.get(key)
        if path:
            if not os.path.exists(path) or os.stat(path).st_size == 0:
                with open(path, 'w') as f:
                    f.write(header + "\n")

def write_full_str(path_ignored:str, full_str:str):
    paths = get_paths()

    # 1. qrStrings.txt = the full string output
    qr_path = paths.get('qr_strings')
    if qr_path:
        with open(qr_path, 'a') as f:
            f.write(strip_commas(full_str) + "\n")

    # Split the QR string into lines
    lines = full_str.strip().split('\n')
    if not lines:
        return

    # 2. SetupList = the first line from a QR string
    setup_path = paths.get('setup_list')
    if setup_path:
        with open(setup_path, 'a') as f:
            f.write(strip_commas(lines[0]) + "\n")

    # 3. EventList = all remaining lines from the QR string
    if len(lines) > 1:
        event_path = paths.get('event_list')
        if event_path:
            with open(event_path, 'a') as f:
                for line in lines[1:]:
                    f.write(strip_commas(line) + "\n")

def replace_last_entry(new_str:str):
    paths = get_paths()

    # We need to remove the last entry from all files.
    # 1. Remove from setupList and capture match info to identify lines in eventList
    setup_path = paths.get('setup_list')
    match_info = None
    if setup_path and os.path.exists(setup_path):
        with open(setup_path, 'r') as f:
            lines = f.readlines()
        if len(lines) > 1:
            last_line = lines[-1].strip().split(',')
            if len(last_line) >= 3:
                match_info = (last_line[0], last_line[1], last_line[2]) # scouter, team, match
            with open(setup_path, 'w') as f:
                f.writelines(lines[:-1])

    # 2. Remove from qrStrings
    qr_path = paths.get('qr_strings')
    if qr_path and os.path.exists(qr_path):
        with open(qr_path, 'r') as f:
            lines = f.readlines()
        if len(lines) > 0:
            with open(qr_path, 'w') as f:
                f.writelines(lines[:-1])

    # 3. Remove from eventList using match info
    if match_info:
        event_path = paths.get('event_list')
        if event_path and os.path.exists(event_path):
            with open(event_path, 'r') as f:
                lines = f.readlines()
            if len(lines) > 0:
                scouter, team, match = match_info
                prefix = f"{scouter},{team},{match},"
                # Keep header (lines[0]) and any lines that don't match the prefix
                new_lines = [lines[0]] + [l for l in lines[1:] if not l.startswith(prefix)]
                with open(event_path, 'w') as f:
                    f.writelines(new_lines)

    # Write the new edited string
    write_full_str("", new_str)

def get_last_full_string():
    paths = get_paths()
    path = paths.get('qr_strings')
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
            if not lines:
                return ""
            return lines[-1].strip()
    except:
        return ""

def get_team_number(full_str:str) -> str:
    try:
        return full_str.split('\n')[0].split(",")[1]
    except:
        return ""

def get_match_number(full_str:str) -> str:
    try:
        return full_str.split('\n')[0].split(",")[2]
    except:
        return ""

# Make sure qr string is a csv value and contains expected keywords
def is_correct_format(full_str:str) -> bool:
    if not full_str:
        return False
    # Check for basic CSV structure
    first_line_values = full_str.split('\n')[0].split(',')
    return len(first_line_values) >= 3
