
from table_view import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np


from table_view import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def prepare_graph_data(selected_temp="T01", default_hours=24):
    data = dashboard_table(selected_temp=selected_temp).copy()

    data["Timestamp"] = pd.to_datetime(
        data["Timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    data = data.dropna(subset=["Timestamp"]).sort_values("Timestamp")

    if data.empty:
        return data

    end_date = data["Timestamp"].max()
    start_date = end_date - pd.Timedelta(hours=default_hours)

    return data[
        (data["Timestamp"] >= start_date) &
        (data["Timestamp"] <= end_date)
    ].copy()


def graph_display(selected_temp="T01", default_hours=24):
    data = prepare_graph_data(selected_temp=selected_temp, default_hours=default_hours)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    ax1, ax2 = axes

    vwc_cols = ["VWC1", "VWC2", "VWC3", "VWC4"]

    for col in vwc_cols:
        if col in data.columns:
            ax1.plot(data["Timestamp"], data[col], label=col)

    ax1.set_title(f"Soil Moisture (VWC1–VWC4) — Last {default_hours} Hours")
    ax1.set_ylabel("VWC")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", ncol=4, frameon=False)

    if selected_temp in data.columns:
        ax2.plot(data["Timestamp"], data[selected_temp], label=selected_temp)

    ax2.set_title(f"Temperature ({selected_temp}) — Last {default_hours} Hours")
    ax2.set_ylabel("°C")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left", frameon=False)

    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))
    ax2.set_xlabel("Time")

    ax1.format_xdata = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
    ax2.format_xdata = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")

    plt.tight_layout()
    return fig

