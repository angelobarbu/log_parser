import re
import zipfile
from io import BytesIO
import os

os.chdir("C:\\Users\\angebarb\\Desktop\\New folder")

with zipfile.ZipFile("diagnostics.zip", "r") as diagnostics:
    for archive_name in diagnostics.namelist():
        if re.search(r'\.zip$', archive_name) != None:
            archive_data = BytesIO(diagnostics.read(archive_name))
            with zipfile.ZipFile(archive_data) as archive:
                for file_name in archive.namelist():
                   print(file_name)


