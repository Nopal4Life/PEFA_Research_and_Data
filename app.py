import streamlit as st

from modules import file_validation as fv
from modules import data_cleaner as dc
from modules import data_visualizer as dv

st.set_page_config(page_title="Data Scrapper and Visualizer", layout="wide")
st.title("Data Scrapper and Visualizer")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("Upload a CSV or Excel file to get started.")
    st.stop()

success, result = fv.validate_file(uploaded_file)
if not success:
    st.error(result)
    st.stop()

raw_df = result

# Reset merge decisions whenever a new file is uploaded.
file_id = (uploaded_file.name, uploaded_file.size)
if st.session_state.get("file_id") != file_id:
    st.session_state.file_id = file_id
    st.session_state.matches = None
    st.session_state.confirmed_merges = []

st.subheader("Data Preview")
st.dataframe(raw_df.head(), use_container_width=True)

st.subheader("Data Summary")
st.dataframe(raw_df.describe(), use_container_width=True)

# --- Missing values ---
st.subheader("Missing Values")
action = st.selectbox("Handle missing values", ["Keep", "Fill", "Drop"])
fill_value = None
if action == "Fill":
    fill_value = st.text_input("Enter fill value")

df = dc.handle_missing_values(raw_df, action, fill_value)

# --- Duplicate / similar-value review ---
st.subheader("Review Similar Values")
categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

col1, col2 = st.columns([2, 1])
with col1:
    selected_cols = st.multiselect(
        "Columns to scan for similar values (leave empty to skip)",
        categorical_cols,
    )
with col2:
    threshold = st.slider("Similarity threshold", min_value=50, max_value=100, value=85)

if st.button("Scan for similar values", disabled=not selected_cols):
    st.session_state.matches = dc.find_fuzzy_matches(df, selected_cols, threshold)

matches = st.session_state.get("matches")

if matches:
    st.write(f"Found {len(matches)} similar value pair(s). Confirm which ones to merge:")
    with st.form("merge_review_form"):
        decisions = {}
        for i, (col, val1, val2, score) in enumerate(matches):
            decisions[i] = st.checkbox(
                f"[{col}] merge '{val2}' into '{val1}' (similarity {score})",
                value=score >= 95,
                key=f"merge_{i}",
            )
        submitted = st.form_submit_button("Apply selected merges")

    if submitted:
        st.session_state.confirmed_merges = [
            (col, val1, val2)
            for i, (col, val1, val2, _score) in enumerate(matches)
            if decisions[i]
        ]
        st.session_state.matches = None
        st.success(f"Applied {len(st.session_state.confirmed_merges)} merge(s).")
elif matches == []:
    st.info("No similar values found above the selected threshold.")

for col, val1, val2 in st.session_state.get("confirmed_merges", []):
    df[col] = df[col].replace(val2, val1)

before = len(df)
df = dc.remove_duplicates(df)
removed = before - len(df)
if removed:
    st.success(f"Removed {removed} exact duplicate row(s).")

# --- Visualization ---
st.subheader("Data Visualization")

df = dv.coerce_datetime_columns(df)
numeric_cols, categorical_cols, datetime_cols = dv.detect_column_types(df)

viz_type = st.selectbox("Choose visualization type", [
    "Histogram (single numeric)",
    "Scatter (numeric vs numeric)",
    "Boxplot (categorical vs numeric)",
    "Time Series (date vs numeric)",
])

try:
    if viz_type == "Histogram (single numeric)" and numeric_cols:
        col = st.selectbox("Select column", numeric_cols)
        st.plotly_chart(dv.plot_histogram(df, col), use_container_width=True)

    elif viz_type == "Scatter (numeric vs numeric)" and len(numeric_cols) >= 2:
        col_x = st.selectbox("Select X axis", numeric_cols)
        col_y = st.selectbox("Select Y axis", numeric_cols, index=1)
        st.plotly_chart(dv.plot_scatter(df, col_x, col_y), use_container_width=True)

    elif viz_type == "Boxplot (categorical vs numeric)" and categorical_cols and numeric_cols:
        cat_col = st.selectbox("Select categorical column", categorical_cols)
        num_col = st.selectbox("Select numeric column", numeric_cols)
        st.plotly_chart(dv.plot_boxplot(df, cat_col, num_col), use_container_width=True)

    elif viz_type == "Time Series (date vs numeric)" and datetime_cols and numeric_cols:
        date_col = st.selectbox("Select date column", datetime_cols)
        num_col = st.selectbox("Select numeric column", numeric_cols, key="ts_num")
        st.plotly_chart(dv.plot_time_series(df, date_col, num_col), use_container_width=True)

    else:
        st.warning("Not enough columns of the right type for this visualization.")
except Exception as e:
    st.error(f"Couldn't render this chart: {e}")
