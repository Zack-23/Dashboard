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

# Previous window for period-over-period comparison (e.g. last 24h vs the 24h before that)
prev_start = start - pd.Timedelta(hours=hours)
prev_view = graph_df[(graph_df["Timestamp"] >= prev_start) & (graph_df["Timestamp"] < start)].copy()

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
    st.plotly_chart(fig_vwc, use_container_width=True)

# --- Probe health detection ---
# A probe is flagged as faulty if its median reading is below -20°C
# (no real soil temperature should be anywhere near that)
FAULT_THRESHOLD = -20.0

available_temps = [t for t in temp_options if t in graph_view.columns]

faulty_probes = {}
healthy_probes = []
for t in available_temps:
    median_val = graph_view[t].median()
    if median_val < FAULT_THRESHOLD:
        faulty_probes[t] = median_val
    else:
        healthy_probes.append(t)

# If removal was requested last run, update selection BEFORE widget renders
if st.session_state.get("pending_remove_faulty", False):
    current = st.session_state.get("temp_graph_select", available_temps)
    st.session_state.temp_graph_select = [t for t in current if t not in faulty_probes]
    st.session_state.pending_remove_faulty = False

# --- Temperature multi-select (always full width) ---
selected_temps = st.multiselect(
    "Temperature probes to display",
    options=available_temps,
    default=available_temps,
    key="temp_graph_select"
)

# Check if any currently selected probes are faulty
active_faulty = {p: faulty_probes[p] for p in selected_temps if p in faulty_probes}

# Show warning ONLY when faulty probes are in the current selection
if active_faulty:
    st.warning("⚠️ **Probe Health Alert** — The following probes are likely disconnected or malfunctioning:")
    alert_cols = st.columns(len(active_faulty))
    for i, (probe, median_val) in enumerate(active_faulty.items()):
        alert_cols[i].markdown(f"🔴 **{probe}**\n\nMedian: **{median_val:.1f}°C**")
    if st.button("Remove faulty probes from analysis", key="remove_faulty_btn"):
        st.session_state.pending_remove_faulty = True
        st.rerun()

# --- Temperature overlay graph ---
if selected_temps:
    temp_long = graph_view[["Timestamp"] + selected_temps].melt(
        id_vars="Timestamp",
        value_vars=selected_temps,
        var_name="Probe",
        value_name="Temperature"
    )
    fig_temp = px.line(
        temp_long,
        x="Timestamp",
        y="Temperature",
        color="Probe",
        title=f"Temperature ({', '.join(selected_temps)}) — Last {hours} hours"
    )
    fig_temp.update_yaxes(title_text="°C")
    st.plotly_chart(fig_temp, use_container_width=True)

    # --- Metric cards: avg temp this window vs previous window ---
    for row_start in range(0, len(selected_temps), 4):
        row_temps = selected_temps[row_start:row_start + 4]
        cols = st.columns(len(row_temps))
        for i, temp in enumerate(row_temps):
            current_avg = graph_view[temp].dropna().mean()
            prev_avg = prev_view[temp].dropna().mean() if temp in prev_view.columns and not prev_view[temp].dropna().empty else None

            if pd.notna(current_avg) and prev_avg is not None:
                delta = current_avg - prev_avg
                cols[i].metric(
                    label=f"{temp} (avg)",
                    value=f"{current_avg:.2f}°C",
                    delta=f"{delta:+.2f}°C vs prev {hours}h"
                )
            elif pd.notna(current_avg):
                cols[i].metric(label=f"{temp} (avg)", value=f"{current_avg:.2f}°C")
            else:
                cols[i].metric(label=f"{temp} (avg)", value="N/A")
else:
    st.info("Select at least one temperature probe to display the graph.")

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
        col = st.selectbox("Metric", numeric_cols, key="single_metric")
        row = stats_row(graph_view[col])
        st.table(pd.DataFrame([row], index=[col]).round(4))

    elif stats_mode == "Stats table":
        default_metrics = [
            c for c in selected_temps + ["VWC1", "VWC2", "VWC3", "VWC4", "VWC_Range"]
            if c in numeric_cols
        ]
        metrics = st.multiselect("Metrics to include", numeric_cols, default=default_metrics, key="stats_metrics")
        stats_dict = {m: stats_row(graph_view[m]) for m in metrics}
        stats_df = pd.DataFrame(stats_dict).T
        stats_df.index.name = "Metric"
        st.dataframe(stats_df.round(4), use_container_width=True)

    else:
        col = st.selectbox("Box plot metric", numeric_cols, key="box_metric")
        fig_box = px.box(graph_view, y=col, points="outliers", title=f"Box Plot of {col}")
        st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# --- Tables ---
tab1, tab2 = st.tabs(["Overview (Recent)", "Full Table"])

with tab1:
    selected_table_temp = st.selectbox("Overview table temperature probe", temp_options, index=0, key="table_temp")

    default_rows = 20
    overview_df = dashboard_table(selected_temp=selected_table_temp).copy()
    overview_df["Timestamp"] = pd.to_datetime(
        overview_df["Timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )
    overview_df = overview_df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    overview_df = overview_df[(overview_df["Timestamp"] >= start) & (overview_df["Timestamp"] <= end)]
    st.dataframe(overview_df.tail(default_rows), use_container_width=True)

with tab2:
    show_adv = st.checkbox("Add advanced columns (Pascal / Teros / Extra Temps)", value=False)

    if show_adv:
        groups = st.multiselect(
            "Choose groups to add",
            ["temperature", "teros", "pascal"],
            default=[],
            key="adv_groups"
        )
        df_table = customized_column(groups, selected_temp="T01").copy()
    else:
        df_table = dashboard_table(selected_temp="T01").copy()

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
            default=df_table.columns.tolist(),
            key="full_table_cols"
        )

        st.dataframe(df_table[cols].head(n), use_container_width=True)

        st.download_button(
            "Download filtered CSV",
            data=df_table[cols].to_csv(index=False).encode("utf-8"),
            file_name="filtered_data.csv",
            mime="text/csv",
        )
