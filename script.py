import re
import zipfile
from io import BytesIO
import os
import pandas as pd
from datetime import datetime
import time
import math
import csv

tic = time.time()
print(f'Started at {datetime.now()}')



os.chdir(os.path.dirname(os.path.abspath(__file__)))

## Unzips the diagnostics.zip archive and extracts the .log files to 'logs' folder ##
with zipfile.ZipFile("diagnostics.zip", "r") as diagnostics:
    for archive_name in diagnostics.namelist():

        # Searches and opens chassis .zip archive
        if re.search(r'\.zip$', archive_name) != None:
            archive_data = BytesIO(diagnostics.read(archive_name))
            with zipfile.ZipFile(archive_data) as archive:

                # Selects and extracts the .log files to 'logs' folder
                files = [file_name for file_name in archive.namelist()
                         if file_name.endswith('.log')]
                for file_name in files:
                    archive.extract(file_name, 'logs')


## Creates a dataframe for log processing ##
data_log = pd.DataFrame(columns=["Timestamp", "File", "Message"])
data_log['Timestamp'] = pd.to_datetime(data_log['Timestamp'])


## Regex identifiers list for multiple timestamp formats ##
timestamp_regex = []
# appinfo_appselector_logcollector_ixiash
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3})')
# ixos_ixserv
timestamp_regex.append(r'([0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})')
# chassis_appsmanager
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})')
# install
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})')
# cloudagent_dpkg
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})')
# ixappsagent
timestamp_regex.append(r'([0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})')
# ixosports
timestamp_regex.append(r'([0-9]{2}_[a-zA-Z]{3}_[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[a-z]{2})')
# db
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}:[0-9]{2}:[0-9]{2})')
# fanrestserver
timestamp_regex.append(r'([0-9]{2} [a-zA-Z]{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})')
# licenseserver
timestamp_regex.append(r'([a-zA-Z]{3} [0-9]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})')
# webplatform
timestamp_regex.append(r'([a-zA-Z]{3} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [a-zA-Z]{3} [0-9]{4})')
# mccstore
timestamp_regex.append(r'([0-9]{4}-[0-9]{2}-[0-9]{2}  [0-9]{2}:[0-9]{2}:[0-9]{2})')
# portsdispatcher
timestamp_regex.append(r'([0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})')


## Deletes the output .log file if already created ##
if os.path.exists('living_hell.log'):
    os.remove('living_hell.log')

## Gets the 'logs' folder path ##
logs_folder = os.path.join(os.getcwd(), 'logs')

## Starts the log processing ##
for root, folders, files in os.walk(logs_folder):
    for file in files:
        path = os.path.join(root, file)
        print(file)
        previous_lines = ""

        # Loads each log file individually
        with open(path) as content:
            var = None

            # Log is processed line by line
            for line in content:
                

                # Sets the timestamp format for the current log file
                if var == None:
                    for key, timestamp in enumerate(timestamp_regex):
                        is_timestamp = re.search(timestamp, line)
                        if is_timestamp != None:
                            var = timestamp
                            index = key
                            break
                else:
                    is_timestamp = re.search(var, line)


                # Writes the timestamp in dataframe according to its format
                if is_timestamp != None:
                    if index == 0:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S,%f')
                    elif index == 1:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%m-%d-%Y %H:%M:%S.%f')
                    elif index == 2:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S.%f')
                    elif index == 3:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%dT%H:%M:%S')
                    elif index == 4:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S')
                    elif index == 5:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%m-%d-%Y %H:%M:%S')
                    elif index == 6:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%d_%b_%Y_%I_%M_%S_%p')
                    elif index == 7:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d_%H:%M:%S')
                    elif index == 8:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%d %b %Y %H:%M:%S')
                    elif index == 9:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%b %d %Y %H:%M:%S')
                    elif index == 10:
                        timestamp = datetime.strptime(
                            (is_timestamp.group(1)[0:15] + is_timestamp.group(1)[19:24]), '%b %d %H:%M:%S %Y')
                    elif index == 11:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d  %H:%M:%S')
                    elif index == 12:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%m/%d/%Y  %H:%M:%S')

                    # Verifies if there is log message before timestamp
                    if is_timestamp.start() != 0:
                        message = line[0:is_timestamp.start()] + line[(is_timestamp.end() + 1):]
                    else:
                        message = line[(is_timestamp.end() + 1):]

                    # Verifies if there are lines that belong to the previous log
                    if previous_lines != "" and len(data_log) != 0:
                        data_log.iloc[(len(data_log) - 1), 2] += previous_lines

                    # Appends log to the dataframe
                    row = pd.DataFrame({'Timestamp': [timestamp], 'File': [
                                       file], 'Message': [message]})
                    data_log = pd.concat(
                        [data_log, row], ignore_index=True, axis=0)
                    previous_lines = ""


                # If no timestamp is found in the current line, the line is a message from the previous log
                else:
                    previous_lines += line

        # Verifies if there are lines that belong to the last log from the file
        if previous_lines != "":
            data_log.iloc[(len(data_log) - 1), 2] += previous_lines

        # Sorts the logs by timestamp asc and exports them file by file
        data_log = data_log.sort_values(by=['Timestamp', 'File'])
        data_log.to_csv('living_hell.log', sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar=' ')



toc = time.time()
print(f'Finished at {datetime.now()}')
print(f'{math.floor((toc - tic) / 3600)}h {math.floor(((toc - tic) % 3600) / 60)}m {(((toc - tic) % 3600) % 60):.3f}s runtime')