import streamlit as st
from utils.data_loader import load_data
from utils.graph_generator import auto_select_graph, generate_graph
from utils.insights import generate_insights
import io

st.set_page_config(page_title="Smart Data Visualiser", layout="wide")

st.title("📊 Smart Data Visualiser")
st.markdown("### 📌 Upload data, explore patterns, and gain insights instantly.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)

    st.subheader("📂 Data Preview")
    st.dataframe(df)

    # =========================
    # FILTERS
    # =========================
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if numeric_cols:
        with st.expander("🎛 Apply Filters"):
            for col in numeric_cols:
                min_val = float(df[col].min())
                max_val = float(df[col].max())

                selected_range = st.slider(
                    f"{col}",
                    min_val,
                    max_val,
                    (min_val, max_val)
                )

                df = df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

    # =========================
    # COLUMN SELECTION (SMART DEFAULTS)
    # =========================
    all_cols = df.columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Smart defaults
    default_x = 0
    default_y = 0

    if categorical_cols:
        default_x = all_cols.index(categorical_cols[0])

    if numeric_cols:
        default_y = all_cols.index(numeric_cols[0])

    col1, col2 = st.columns(2)

    with col1:
        x_col = st.selectbox("Select X-axis", all_cols, index=default_x)

    with col2:
        y_col = st.selectbox("Select Y-axis", all_cols, index=default_y)

    # =========================
    # UX GUIDANCE (NOT BLOCKING)
    # =========================
    if x_col == y_col:
        if x_col in numeric_cols:
            st.info("You're analyzing distribution of a single variable → Histogram will be used.")
        else:
            st.info("Same column selected → Consider choosing a numeric column for better insights.")

    # =========================
    # GRAPH TYPE
    # =========================
    graph_option = st.selectbox(
        "Graph Type",
        ["Auto", "Bar", "Line", "Pie", "Scatter", "Histogram"]
    )

    # =========================
    # VALIDATION + AUTO LOGIC
    # =========================
    if graph_option != "Auto":

        graph_type = graph_option.lower()

        if graph_type in ["bar", "line", "pie"] and y_col not in numeric_cols:
            st.error("Selected graph requires numeric Y-axis")
            st.stop()

        if graph_type == "scatter":
            if x_col not in numeric_cols or y_col not in numeric_cols:
                st.error("Scatter requires both X and Y numeric")
                st.stop()

        if graph_type == "histogram":
            if y_col not in numeric_cols:
                st.error("Histogram requires numeric column")
                st.stop()

    else:
        graph_type = auto_select_graph(df, x_col, y_col)

        # Smart fallback handling
        if graph_type in ["bar", "line", "pie"] and y_col not in numeric_cols:
            st.warning("Auto-adjusted: switched to BAR (numeric Y required)")
            graph_type = "bar"

        if graph_type == "scatter":
            if x_col not in numeric_cols or y_col not in numeric_cols:
                st.warning("Auto-adjusted: scatter → BAR")
                graph_type = "bar"

        if graph_type == "histogram":
            if y_col not in numeric_cols:
                st.warning("Auto-adjusted: histogram → BAR")
                graph_type = "bar"

    # =========================
    # GRAPH DISPLAY
    # =========================
    fig = generate_graph(df, x_col, y_col, graph_type)

    st.subheader("📈 Graph")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(fig)

    # =========================
    # HEATMAP (ADVANCED SECTION)
    # =========================
    if len(numeric_cols) >= 2 and graph_type!="heatmap" :
        st.subheader("📊 Correlation Heatmap")

        heatmap_fig = generate_graph(df, x_col, y_col, "heatmap")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.pyplot(heatmap_fig)

    # =========================
    # INSIGHTS
    # =========================
    st.subheader("🧠 Insights")

    insights = generate_insights(df, x_col, y_col, graph_type)

    for i in insights:
        st.write(f"• {i}")

    # =========================
    # DOWNLOAD
    # =========================
    buf = io.BytesIO()
    fig.savefig(buf, format="png")

    st.download_button(
        label="📥 Download Graph",
        data=buf.getvalue(),
        file_name="graph.png",
        mime="image/png"
    )