
import dropbox
import pandas as pd
from io import StringIO
import numpy as np
from pathlib import Path
import os
from dropbox.files import FileMetadata


# Icfar-Dashboard
# Access token
# so far achieved to read the data from the dropbox and print the content of the file.

# using refresh tokens so i can have permanent access.

# I got the refresh token by using the URL including client id and it
# the refresh token to a redirected fake server to deliver the authorizaed code
# sent it to the powershell.

REFRESH_TOKEN = "IbAzVJKd9sQAAAAAAAAAAbwv1JHzh9rkqQDT0HjUzocAs2kiEszshFai9AiK2-Sq"
APP_KEY = "5cwf3yjmkgtzdr9"
APP_SECRET = "lzh93ghd4mwh0rm"

dropbox_access = dropbox.Dropbox(
    # this refreshes the access token.
    # accessing the dropbox
    # python requests refresh access token each time.
    oauth2_refresh_token=REFRESH_TOKEN,
    app_key=APP_KEY,
    app_secret=APP_SECRET
)

def get_recent_file():
    # This functions gets the recent files from the dropbox given the access token.
    actual_path = "/WIRED/Site0_Montreal/RDL/USB0"
    date_folders = dropbox_access.files_list_folder(actual_path)
    sorted_folders = [i for i in date_folders.entries]
    latest_folder = None
    for entry in sorted_folders:
        # add ininstance.
        if latest_folder is None:
            latest_folder = entry
        else:
            if entry.name > latest_folder.name:
                latest_folder = entry
    if latest_folder is None:
        raise RuntimeError("No folders have been found")

    folder_path = latest_folder.path_lower # converting to the actual path
    files_in_folder = dropbox_access.files_list_folder(folder_path)
    latest_file = None
    for entries in files_in_folder.entries:
        # add an isinstance method.
        if latest_file is None:
            latest_file = entries
        else:
            if entries.name > latest_file.name:
                latest_file = entries
        if latest_file is None:
            raise RuntimeError("No file has been found")
    file_path = latest_file.path_lower
    return [file_path, dropbox_access] # return the file path and dropbox access
def analyze_file_content(files_content):
    open_file = files_content[1].files_download(files_content[0])
    content_file = open_file[1].content.decode("utf-8", errors="replace")
    lines = content_file.splitlines()
    for line in lines:
        print(line)

file = get_recent_file()
analyze_file_content(file)








