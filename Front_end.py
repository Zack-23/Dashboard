
import streamlit as st
from graph_view import *
from table_view import *
import plotly.express as px

st.title("Sensor Dashboard")
st.write("Soil moisture + temperature overview and statistics")

# code below is meant for graph display
df = dashboard_table().copy()
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y/%m/%d %H:%M:%S", errors="coerce")
df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp")

hours = st.selectbox("Time window (hours)", [24, 72, 168, 336], index=0)
end = df["Timestamp"].max()
start = end - pd.Timedelta(hours=hours)
view = df[(df["Timestamp"] >= start) & (df["Timestamp"] <= end)]

vwc_cols = [c for c in ["VWC1", "VWC2", "VWC3", "VWC4"] if c in view.columns]
temp_col = "Average_Temp" if "Average_Temp" in view.columns else None

# melt VWC so Plotly can plot multiple lines easily
vwc_long = view[["Timestamp"] + vwc_cols].melt(
    id_vars="Timestamp", value_vars=vwc_cols, var_name="Sensor", value_name="VWC"
)

fig_vwc = px.line(vwc_long, x="Timestamp", y="VWC", color="Sensor",
                  title=f"Soil Moisture (VWC1–VWC4) — Last {hours} hours")
st.plotly_chart(fig_vwc, use_container_width=True)

if temp_col:
    fig_temp = px.line(view, x="Timestamp", y=temp_col,
                       title=f"Temperature — Last {hours} hours")
    st.plotly_chart(fig_temp, use_container_width=True)

st.divider()
# This portion is responsible for statistical display.
st.subheader("Summary Statistics")

# Choose what to summarize
stats_mode = st.radio("Stats view", ["Single metric", "Stats table", "Box plot"], horizontal=True)

numeric_cols = view.select_dtypes(include="number").columns.tolist()

def stats_row(series):
    s = series.dropna()
    if s.empty:
        return {"Mean": None, "Median": None, "Min": None, "Max": None, "Std": None}
    return {
        "Mean": s.mean(),
        "Median": s.median(),
        "Min": s.min(),
        "Max": s.max(),
        "Std": s.std(ddof=1) if len(s) > 1 else 0.0,
    }

if not numeric_cols:
    st.warning("No numeric columns available for statistics.")
else:
    if stats_mode == "Single metric":
        col = st.selectbox("Metric", numeric_cols)
        row = stats_row(view[col])
        st.table(pd.DataFrame([row], index=[col]).round(4))

    elif stats_mode == "Stats table":
        default_metrics = [c for c in ["Average_Temp", "VWC1", "VWC2", "VWC3", "VWC4", "VWC_Range"] if
                           c in numeric_cols]
        metrics = st.multiselect("Metrics to include", numeric_cols, default=default_metrics)

        stats_dict = {m: stats_row(view[m]) for m in metrics}
        stats_df = pd.DataFrame(stats_dict).T
        stats_df.index.name = "Metric"
        st.dataframe(stats_df.round(4), use_container_width=True)

    else:  # Box plot
        col = st.selectbox("Box plot metric", numeric_cols)
        fig_box = px.box(view, y=col, points="outliers", title=f"Box Plot of {col}")
        st.plotly_chart(fig_box, use_container_width=True)

st.divider()
# default table below
tab1, tab2 = st.tabs(["Overview (Recent)", "Full Table"])

with tab1:
    default_rows = 20
    view_sorted = view.sort_values("Timestamp")
    view_sorted = view.sort_values("Timestamp").reset_index(drop=True)
    st.dataframe(view_sorted.tail(default_rows), use_container_width=True)

with tab2:
    # 1) Choose base table (default vs advanced)
    show_adv = st.checkbox("Add advanced columns (Pascal / Teros / Raw Temps)", value=False)

    groups = []
    if show_adv:
        groups = st.multiselect(
            "Choose groups to add",
            ["temperature", "teros", "pascal"],
            default=[]
        )
        df_table = customized_column(groups).copy()  # uses base_table underneath
    else:
        df_table = dashboard_table().copy()

    # 2) Parse + sort + reset index for clean row numbers
    df_table["Timestamp"] = pd.to_datetime(df_table["Timestamp"], errors="coerce")
    df_table = df_table.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)

    # 3) Apply the SAME time window filter you used for graphs
    df_table = df_table[(df_table["Timestamp"] >= start) & (df_table["Timestamp"] <= end)]

    if len(df_table) == 0:
        st.warning("No rows in this time window.")
    else:
        # 4) Rows + columns controls
        n = st.slider("Rows to show (from start)", 10, len(df_table), min(200, len(df_table)))

        cols = st.multiselect(
            "Columns to show",
            options=df_table.columns.tolist(),
            default=df_table.columns.tolist()
        )

        st.dataframe(df_table[cols].head(n), use_container_width=True)

        st.download_button(
            "Download filtered CSV",
            data=df_table[cols].to_csv(index=False).encode("utf-8"),
            file_name="filtered_data.csv",
            mime="text/csv",
        )