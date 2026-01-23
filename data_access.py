
import re
import pandas as pd


def clean_data():
    # This function reads the messy data and stores it in a clean table
    # that we can work with and other functions can deal with.
    filename = "RDL_2025-09-01_USB0.txt"
    output_file = "clean_data"
    header = (
        "Date Std_Time Sample "
        "T01 T02 T03 T04 T05 T06 T07 T08 "
        "Teros1_mV VWC1 Pascal1 "
        "Teros2_mV VWC2 Pascal2 "
        "Teros3_mV VWC3 Pascal3 "
        "Teros4_mV VWC4 Pascal4\n"
    )
    pattern = r"\d{4}/\d{2}/\d{2}" # this searches for the correct date.
    with open(filename, "r") as file, open(output_file, "w") as output:
        output.write(header)
        for line in file:
            match = re.search(pattern, line) # finding the correct start of the data and ignoring anything before.
            if not match:
                continue # ignore if correct data has not been found.
            clean_line = line[match.start():].strip()
            parts = clean_line.split()
            parts = [p for p in parts if p != "*"]
            parts = parts[:-2]
            output.write(" ".join(parts) + "\n")
def load_clean_data():
    # This function stores the information in pandas table.
    df = pd.read_csv("clean_data", sep=r"\s+")
    return df

def get_recent_rows(value = 10, full_data = False):
    # This function handles the rows show in the UI, the default is last 10 rows.
    data_control = load_clean_data() # get the pandas table.
    if full_data: # if full view of data has been requested return entire rows.
        return data_control

    else:
        return data_control.head(value)




