from cmath import nan
import re
import zipfile
from io import BytesIO
import os
import pandas as pd
from datetime import datetime
import time
import math

tic = time.time()
print(f'Started at {datetime.now()}')

os.chdir("C:\\Users\\angebarb\\Desktop\\mic_script")

## Unzips the diagnostics.zip archive and extracts the .log files to 'logs' folder ##
with zipfile.ZipFile("diagnostics.zip", "r") as diagnostics:
    for archive_name in diagnostics.namelist():
        # Searches for and opens chassis .zip archive #
        if re.search(r'\.zip$', archive_name) != None:
            archive_data = BytesIO(diagnostics.read(archive_name))
            with zipfile.ZipFile(archive_data) as archive:
                # Selects and extracts the .log files to 'logs' folder #
                files = [file_name for file_name in archive.namelist()
                         if file_name.endswith('.log')]
                for file_name in files:
                    archive.extract(file_name, 'logs')

## Loads the extracted logs from 'logs' folder ##
logs_folder = os.path.join(os.getcwd(), 'logs')

## Deletes the output .log file if already created ##
if os.path.exists('living_hell.log'):
    os.remove('living_hell.log')


# logs = []
# log_files = []
# x = re.search(timestamp2_regex, "2019-09-27 19:35:24,598 - install - INFO - >>>>>>>>>>>>>>>>>>>>>>>>>> Install started!")
# print(x.group(0))

# print(x.group(1))
# match = re.search(regex, " here at 27-05-2020 15:30:24 could not open this file for real")
# timestamp = re.search(regex, " here at could not open this file for real")
# print(timestamp)
# print(timestamp.group(1))
# print(re.findall(" here at 27-05-2020 15:30:24 could not open this file for real"))


## Creates a dataframe for log processing ##
data_log = pd.DataFrame(columns=["Timestamp", "File", "Message"])
data_log['Timestamp'] = pd.to_datetime(data_log['Timestamp'])


# row = pd.DataFrame({'Timestamp': ['2022-07-23 17:45:00'], 'File': ['ex.log'], 'Message': ['thats a message']})
# data_log = pd.concat([data_log, row], ignore_index=True, axis=0)
# print(len(data_log))
# print(data_log['Timestamp'][0])
# ixos: Time 13_Jun_2022_04_10_12_pm
# ixia_fan_control, licenseserverplus, webplatform


## Regex identifiers for multiple timestamp formats ##
timestamp_regex = [0, 0, 0, 0, 0, 0]
# ixiaapps_agent
timestamp_regex[0] = r'([0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})'
# appinfo&appselector
timestamp_regex[1] = r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3})'
# chassis
timestamp_regex[2] = r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})'
# cloud_agent
timestamp_regex[3] = r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})'
# install
timestamp_regex[4] = r'([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})'
# ixos_ixserv
timestamp_regex[5] = r'([0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})'

for root, folders, files in os.walk(logs_folder):

    for file in files:
        path = os.path.join(root, file)
        print(file)
        previous_lines = ""
        with open(path) as content:
            var = None
            for line in content:

                if var == None:

                    for key, timestamp in enumerate(timestamp_regex):
                        is_timestamp = re.search(timestamp, line)
                        if is_timestamp != None:
                            var = timestamp
                            index = key
                            break
                else:
                    is_timestamp = re.search(var, line)

                if is_timestamp != None:
                    if index == 0:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%m-%d-%Y %H:%M:%S')
                    elif index == 1:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S,%f')
                    elif index == 2:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S.%f')
                    elif index == 3:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%d %H:%M:%S')
                    elif index == 4:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%Y-%m-%dT%H:%M:%S')
                    elif index == 5:
                        timestamp = datetime.strptime(
                            is_timestamp.group(1), '%m-%d-%Y %H:%M:%S.%f')

                    message = line[(is_timestamp.end() + 1):]

                    if previous_lines != "":
                        data_log['Message'][(
                            len(data_log) - 1)] += previous_lines
                    row = pd.DataFrame({'Timestamp': [timestamp], 'File': [
                                       file], 'Message': [message]})
                    data_log = pd.concat(
                        [data_log, row], ignore_index=True, axis=0)
                    previous_lines = ""
                else:
                    previous_lines += line

        if previous_lines != "":
            data_log['Message'][(len(data_log) - 1)] += previous_lines

data_log = data_log.sort_values(by=['Timestamp', 'File'])
data_log.to_csv('living_hell.log', sep='\t', index=False, header=False)

        # print(timestamp)
        # timestamp = line.strip().split(" - ")[0]
        # print(line_stripped[0])
        # row = pd.DataFrame({'Timestamp': [timestamp], 'File': [file], 'Message': [message]})
        # print(row)
        # data_log = pd.concat([data_log, row], ignore_index=True, axis=0)
        # data_log['Content'] = line_stripped[1:]
        # logs.append(content.read())
        # log_files.append(file)


toc = time.time()

print(f'Finished at {datetime.now()}')
print(f'{math.floor((toc - tic) / 3600)}h {math.floor(((toc - tic) % 3600) / 60)}m {(((toc - tic) % 3600) % 60):.3f}s runtime')


#data_log.to_csv('living_hell.log', index=False)

# for log, i in log_files:
# for line in logs[0]:
    # print(line)

# print(log_files[0])
# print(logs[0])
# Writes all logs to a dummy .log file and removes the prev dummy
# if os.path.exists('living_hell.log'):
#    os.remove('living_hell.log')

#data_log.to_csv('living_hell.log', sep='\t', index=False, header=False)
# log_file = open('living_hell.log', 'a')

# for i in range(len(logs)):
#    log_file.write(logs[i])
#    log_file.write('\n')
