import numpy as np
from data_access import *

# This file handles coloumns of the table, what should the user see
# and customizable options.

table_data = load_clean_data()
COLUMN_GROUPS = {
    "temperature": ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
    "teros": ["Teros1_mV", "Teros2_mV", "Teros3_mV", "Teros4_mV"],
    "pascal": ["Pascal1", "Pascal2", "Pascal3", "Pascal4"],
}

def clean_table(df):
    # this function cleans the table and takes out negative values especially temperature values
    # and replaces them with nan this is to ensure panda ignores it when calculating.
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].where(df[numeric_cols] >= 0, np.nan)
    return df

def base_table():
    df = clean_table(table_data.copy())
    TEMP_COLS = [c for c in df.columns if c.startswith("T") and len(c) == 3]
    VWC_COLS = ["VWC1", "VWC2", "VWC3", "VWC4"]

    df["Timestamp"] = df["Date"] + " " + df["Std_Time"]

    if TEMP_COLS:
        df["Average_Temp"] = df[TEMP_COLS].mean(axis=1)

    if all(c in df.columns for c in VWC_COLS):
        df["VWC_Range"] = df[VWC_COLS].max(axis=1) - df[VWC_COLS].min(axis=1)

    return df
def dashboard_table():
    # This function handles the display rows for the dashboard table.
    # it handles defaults columns
    DEFAULT_COLUMNS = [ "Timestamp",
        "Average_Temp",
        "VWC1",
        "VWC2",
        "VWC3",
        "VWC4",
        "VWC_Range",]
    dashboard_data = base_table()
    cols = [i for i in DEFAULT_COLUMNS if i in dashboard_data.columns]
    return dashboard_data[cols]

def customized_column(options = None):
    COLUMN_GROUPS = {
        "temperature": ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
        "teros": ["Teros1_mV", "Teros2_mV", "Teros3_mV", "Teros4_mV"],
        "pascal": ["Pascal1", "Pascal2", "Pascal3", "Pascal4"],
    }
    DEFAULT_COLUMNS = [
        "Timestamp",
        "Average_Temp",
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