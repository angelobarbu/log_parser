import re
import zipfile
from io import BytesIO
import os
import pandas as pd

os.chdir("C:\\Users\\angebarb\\Desktop\\mic_script")

# Opens diagnostics.zip archive
with zipfile.ZipFile("diagnostics.zip", "r") as diagnostics:
    for archive_name in diagnostics.namelist():
        # Searches for and opens chassis .zip archive
        if re.search(r'\.zip$', archive_name) != None: 
            archive_data = BytesIO(diagnostics.read(archive_name))
            with zipfile.ZipFile(archive_data) as archive:
                # Selects and extracts the .log files
                files = [file_name for file_name in archive.namelist() if file_name.endswith('.log')]
                for file_name in files:
                    archive.extract(file_name, 'logs')


logs_folder = os.path.join(os.getcwd(), 'logs')

#print(len(list(os.walk(logs_folder))))

# Takes each log file and adds to logs list
logs = []
for root, folders, files in os.walk(logs_folder):
    for file in files:
        path = os.path.join(root, file)
        with open(path) as content:
            logs.append(content.read())

print(len(logs))
#print(type(logs))
