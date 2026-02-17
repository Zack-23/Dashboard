
from table_view import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np


def graph_display(default_hours = 24):
    # This function displays time series of the data.
    data = dashboard_table()

    # grab valid date formats
    data["Timestamp"] = pd.to_datetime(data["Timestamp"], format="%Y/%m/%d %H:%M:%S",
        errors="coerce") # convert to actual time

    date = data.dropna(subset=["Timestamp"]).sort_values("Timestamp") # sort values

    # working with the last 24 hours.
    end_date = date["Timestamp"].max()
    start_date = end_date - pd.Timedelta(hours=default_hours)
    correct_date = date[(date["Timestamp"] >= start_date) & (date["Timestamp"] <= end_date)].copy()

    result = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig = result[0]
    axes = result[1]
    ax1 = axes[0]
    ax2 = axes[1]
    vwc_cols = ["VWC1", "VWC2", "VWC3", "VWC4"]
    missing = {}
    # first graph below contains vwc1 up to vwc4.
    for c in vwc_cols:
        if c in correct_date.columns:
            ax1.plot(correct_date["Timestamp"], correct_date[c], label=c)
        else:
            missing[c] = True
    ax1.set_title("Soil Moisture (VWC1–VWC4) — Last 24 Hours")
    ax1.set_ylabel("VWC")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", ncol=4, frameon=False)
    # second graph containing temperature.
    if "Average_Temp" in correct_date.columns:
        ax2.plot(correct_date["Timestamp"], correct_date["Average_Temp"], label="Temperature")
    ax2.set_title("Temperature - Last 24 Hours")
    ax2.set_ylabel("°C")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left", frameon=False)

    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))
    ax2.set_xlabel("Time")
    plt.tight_layout()
    ax1.format_xdata = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
    ax2.format_xdata = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
    return fig

def graph_display2():
    # This function displays histogram.
    data = dashboard_table()
    data["Timestamp"] = pd.to_datetime(
        data["Timestamp"], format="%Y/%m/%d %H:%M:%S", errors="coerce")

    col = "Average_Temp"
    new_data = data[col].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(new_data, bins="auto", edgecolor="black")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Histogram of {col}")
    fig.tight_layout()
    return fig


