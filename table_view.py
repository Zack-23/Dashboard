import numpy as np
from data_access import *

# This file handles coloumns of the table, what should the user see
# and customizable options.

table_data = load_clean_data() # accessing panda table.

COLUMN_GROUPS = {
    "temperature": ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
    "teros": ["Teros1_mV", "Teros2_mV", "Teros3_mV", "Teros4_mV"],
    "pascal": ["Pascal1", "Pascal2", "Pascal3", "Pascal4"],
}



def base_table():
    df = table_data
    # all Temperature columns.
    TEMP_COLS = [c for c in df.columns if c.startswith("T") and len(c) == 3]
    VWC_COLS = ["VWC1", "VWC2", "VWC3", "VWC4"]

    # calculating timestamp
    df["Timestamp"] = df["Date"] + " " + df["Std_Time"]

    # calculating average temperature only if temp columns exist.
    if all(c in df.columns for c in VWC_COLS):
        df["VWC_Range"] = df[VWC_COLS].max(axis=1) - df[VWC_COLS].min(axis=1) # including VWC range column in panda table.

    return df # returning the cleaned panda table.


def dashboard_table(selected_temp = "T01"):
    # This function handles the display rows for the dashboard table.
    # it handles defaults columns
    DEFAULT_COLUMNS = DEFAULT_COLUMNS = [
    "Timestamp",
    selected_temp,
    "VWC1",
    "VWC2",
    "VWC3",
    "VWC4",
    "VWC_Range",
]
    dashboard_data = base_table()
    cols = [i for i in DEFAULT_COLUMNS if i in dashboard_data.columns] # if default columns exist in panda table
    # return it

    return dashboard_data[cols]

def customized_column(options = None, selected_temp = "T01"):
    # all possible columns
    COLUMN_GROUPS = {
        "temperature": ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
        "teros": ["Teros1_mV", "Teros2_mV", "Teros3_mV", "Teros4_mV"],
        "pascal": ["Pascal1", "Pascal2", "Pascal3", "Pascal4"],
    }
    # showcasing this as default columns
    DEFAULT_COLUMNS = [
        "Timestamp",
        selected_temp,
        "VWC1",
        "VWC2",
        "VWC3",
        "VWC4",
        "VWC_Range",
    ]

    dashboard_data = base_table()

    if options is None: # so we dont get into error assign it to empty list.
        options = []

    selected_columns = list(DEFAULT_COLUMNS) # make a copy list.

    for group in options:
        if group in COLUMN_GROUPS:
            selected_columns.extend(COLUMN_GROUPS[group]) # if the option is found we extend the default options.

    # remove duplicates, preserve order
    selected_columns =  [c for c in selected_columns if c in dashboard_data.columns]
    return dashboard_data[selected_columns]

def temp_status_row(row, temp_cols):
    # complete this  # later changes.
    missing = [col for col in temp_cols if pd.isna(row[col])]

    if missing:
        return f"Missing {missing[0]}"
    return "OK"

if __name__ == "__main__":
    table = dashboard_table()
    print(table)
    print("\n--- INFO ---")
    print(table.info())