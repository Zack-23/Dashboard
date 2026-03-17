import streamlit as st
from table_view import *
import pandas as pd
import plotly.express as px

st.title("Sensor Dashboard")
st.write("Soil moisture + temperature overview and statistics")

# --- Time window only at the top ---
hours = st.selectbox("Time window (hours)", [24, 72, 168, 336], index=0)

temp_options = [f"T0{i}" for i in range(1, 9)]

# base data for graphs
graph_df = base_table().copy()
graph_df["Timestamp"] = pd.to_datetime(
    graph_df["Timestamp"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"
)
graph_df = graph_df.dropna(subset=["Timestamp"]).sort_values("Timestamp")

if graph_df.empty:
    st.warning("No valid timestamped data available.")
    st.stop()

end = graph_df["Timestamp"].max()
start = end - pd.Timedelta(hours=hours)
graph_view = graph_df[(graph_df["Timestamp"] >= start) & (graph_df["Timestamp"] <= end)].copy()

# --- VWC Graph ---
vwc_cols = [c for c in ["VWC1", "VWC2", "VWC3", "VWC4"] if c in graph_view.columns]

if vwc_cols:
    vwc_long = graph_view[["Timestamp"] + vwc_cols].melt(
        id_vars="Timestamp",
        value_vars=vwc_cols,
        var_name="Sensor",
        value_name="VWC"
    )
    fig_vwc = px.line(
        vwc_long,
        x="Timestamp",
        y="VWC",
        color="Sensor",
        title=f"Soil Moisture (VWC1–VWC4) — Last {hours} hours"
    )
    st.plotly_chart(fig_vwc, width="stretch")

# --- Temperature selector right above the temp graph ---
selected_graph_temp = st.selectbox("Graph temperature probe", temp_options, index=0)
temp_col = selected_graph_temp if selected_graph_temp in graph_view.columns else None

if temp_col:
    fig_temp = px.line(
        graph_view,
        x="Timestamp",
        y=temp_col,
        title=f"Temperature ({temp_col}) — Last {hours} hours"
    )
    st.plotly_chart(fig_temp, width="stretch")

st.divider()

# --- Statistics ---
st.subheader("Summary Statistics")
stats_mode = st.radio("Stats view", ["Single metric", "Stats table", "Box plot"], horizontal=True)

numeric_cols = graph_view.select_dtypes(include="number").columns.tolist()

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
        row = stats_row(graph_view[col])
        st.table(pd.DataFrame([row], index=[col]).round(4))

    elif stats_mode == "Stats table":
        default_metrics = [
            c for c in [selected_graph_temp, "VWC1", "VWC2", "VWC3", "VWC4", "VWC_Range"]
            if c in numeric_cols
        ]
        metrics = st.multiselect("Metrics to include", numeric_cols, default=default_metrics)
        stats_dict = {m: stats_row(graph_view[m]) for m in metrics}
        stats_df = pd.DataFrame(stats_dict).T
        stats_df.index.name = "Metric"
        st.dataframe(stats_df.round(4), width="stretch")

    else:
        col = st.selectbox("Box plot metric", numeric_cols)
        fig_box = px.box(graph_view, y=col, points="outliers", title=f"Box Plot of {col}")
        st.plotly_chart(fig_box, width="stretch")

st.divider()

# --- Tables ---
tab1, tab2 = st.tabs(["Overview (Recent)", "Full Table"])

with tab1:
    # Temperature selector right here in the table section
    selected_table_temp = st.selectbox("Overview table temperature probe", temp_options, index=0)

    default_rows = 20
    overview_df = dashboard_table(selected_temp=selected_table_temp).copy()
    overview_df["Timestamp"] = pd.to_datetime(
        overview_df["Timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )
    overview_df = overview_df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    overview_df = overview_df[(overview_df["Timestamp"] >= start) & (overview_df["Timestamp"] <= end)]
    st.dataframe(overview_df.tail(default_rows), width="stretch")

with tab2:
    show_adv = st.checkbox("Add advanced columns (Pascal / Teros / Extra Temps)", value=False)

    if show_adv:
        groups = st.multiselect(
            "Choose groups to add",
            ["temperature", "teros", "pascal"],
            default=[]
        )
        df_table = customized_column(groups, selected_temp="T01").copy()
    else:
        df_table = dashboard_table(selected_temp="T01").copy()

    # Fix duplicate columns before anything else
    df_table = df_table.loc[:, ~df_table.columns.duplicated()]

    df_table["Timestamp"] = pd.to_datetime(
        df_table["Timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )
    df_table = df_table.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    df_table = df_table[(df_table["Timestamp"] >= start) & (df_table["Timestamp"] <= end)]

    if len(df_table) == 0:
        st.warning("No rows in this time window.")
    else:
        n = st.slider("Rows to show (from start)", 10, len(df_table), min(200, len(df_table)))

        cols = st.multiselect(
            "Columns to show",
            options=df_table.columns.tolist(),
            default=df_table.columns.tolist()
        )

        st.dataframe(df_table[cols].head(n), width="stretch")

        st.download_button(
            "Download filtered CSV",
            data=df_table[cols].to_csv(index=False).encode("utf-8"),
            file_name="filtered_data.csv",
            mime="text/csv",
        )