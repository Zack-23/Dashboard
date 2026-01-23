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


def temp_status_row(row, temp_cols):
    # complete this.
    missing = [col for col in temp_cols if pd.isna(row[col])]

    if missing:
        return f"Missing {missing[0]}"
    return "OK"


def dashboard_table():
    # This function handles the display rows for the dashboard table.
    dashboard_data = table_data.copy()
    cleaned_dashboard = clean_table(dashboard_data)

    TEMP_COLS = [
        c for c in cleaned_dashboard.columns
        if c.startswith("T") and len(c) == 3
    ]
    VWC_COLS = ["VWC1", "VWC2", "VWC3", "VWC4"]

    dashboard_data["Average_Temp"] = cleaned_dashboard[TEMP_COLS].mean(axis=1)

    cleaned_dashboard["Timestamp"] = (
            cleaned_dashboard["Date"] + " " + cleaned_dashboard["Std_Time"]
    )

    cleaned_dashboard["VWC_Range"] = (
            cleaned_dashboard[VWC_COLS].max(axis=1)
            - cleaned_dashboard[VWC_COLS].min(axis=1)
    )
    DEFAULT_COLUMNS = [
        "Timestamp",
        "Average_Temp",
        "VWC1",
        "VWC2",
        "VWC3",
        "VWC4",
        "VWC_Range",
    ]
    return cleaned_dashboard[DEFAULT_COLUMNS]

def customized_column(options = None):
    OPTIONAL_COLUMNS = {
        "temperatures": ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
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
    dashboard_data = dashboard_table()

    if options is None: # so we dont get into error assign it to empty list.
        options = []
    selected_columns = list(DEFAULT_COLUMNS) # make a copy list.

    for group in options:
        if group in OPTIONAL_COLUMNS:
            selected_columns.extend(COLUMN_GROUPS[group]) # if the option is found we extend the default options.

    # remove duplicates, preserve order
    selected_columns = list(dict.fromkeys(selected_columns))
    return dashboard_data[selected_columns]

if __name__ == "__main__":
    table = dashboard_table()
    print(table.head(10))
    print("\n--- INFO ---")
    print(table.info())