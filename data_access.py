import re
import glob
import pandas as pd
from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient # library allows us to connect to Azure storage and read files.
load_dotenv()

connection_string = os.getenv("AZURE_CONNECTION_STRING") # get the connection string.
container_name = "project-files" # get the container name from Azure.



def clean_data():
    blob_service = BlobServiceClient.from_connection_string(connection_string) # connect to the azure storage
    container = blob_service.get_container_client(container_name) # get the container or folder.

    blobs = list(container.list_blobs()) # get all files from the container
    if not blobs:
        print("Warning: No files found in container.")
        return

    output_file = "clean_data"
    header = (
        "Date Std_Time Sample "
        "T01 T02 T03 T04 T05 T06 T07 T08 "
        "Teros1_mV VWC1 Pascal1 "
        "Teros2_mV VWC2 Pascal2 "
        "Teros3_mV VWC3 Pascal3 "
        "Teros4_mV VWC4 Pascal4\n"
    )
    pattern = r"\d{4}/\d{2}/\d{2}" # finding valid rows.

    with open(output_file, "w") as output:
        output.write(header)

        for blob in blobs:
            blob_client = container.get_blob_client(blob.name) # get access to the file
            content = blob_client.download_blob().readall().decode("utf-8") # dowload the file content and make it into readable form

            for line in content.splitlines():
                valid_line = re.search(pattern, line)
                if not valid_line:
                    continue

                clean_line = line.strip()
                parts = clean_line.split()
                cols = []
                skip_next = False

                for check in parts:
                    if skip_next:
                        skip_next = False
                        continue
                    if check == "*":
                        continue
                    match = re.fullmatch(pattern, check)
                    if match:
                        skip_next = True
                        continue
                    else:
                        cols.append(check)

                cols = cols[:-2]
                if len(cols) != 23:
                    continue

                output.write(" ".join(cols) + "\n")


def load_clean_data():
    # This function stores the information in pandas table.
    df = pd.read_csv("clean_data", sep=r"\s+")  # load the text file into pandas.
    # the sep separate columns by spaces
    return df

def get_recent_rows(value = 10, full_data = False):
    # This function handles the rows show in the UI, the default is last 10 rows.
    data_control = load_clean_data()  # get the pandas table.

    if full_data:  # if full view of data has been requested return entire rows.
        return data_control
    else:
        return data_control.head(value)


clean_data()