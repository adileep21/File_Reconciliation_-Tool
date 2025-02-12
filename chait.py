import os
import pandas as pd
import streamlit as st
from io import BytesIO

 
# Set Streamlit page configuration
st.set_page_config(
    page_title="📑 File Operations Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Ensure a temporary directory exists
TEMP_DIR = "temp_uploaded_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to Convert DataFrame to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
 
# Cache data to improve speed
@st.cache_data(show_spinner=False)
def read_csv(file):
    """Read a CSV file."""
    try:
        return pd.read_csv(file, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None
 
@st.cache_data(show_spinner=False)
def read_excel(file):
    """Read an Excel file and return sheet names."""
    try:
        excel_file = pd.ExcelFile(file, engine="openpyxl")
        return excel_file.sheet_names
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None
 
def load_excel_sheet(file, sheet_name):
    """Load a specific sheet from an Excel file."""
    try:
        return pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading sheet '{sheet_name}': {e}")
        return None
 
@st.cache_data(show_spinner=False)
def validate_columns(dfs):
    """Check if all dataframes have identical columns."""
    columns_list = [set(df.columns) for df in dfs]
    return all(cols == columns_list[0] for cols in columns_list)
 
@st.cache_data(show_spinner=False)
def append_files(files, selected_sheets):
    """Append files while validating column consistency."""
    dfs = []
    for file in files:
        if file.name.endswith(("xlsx", "xls")):
            sheet_name = selected_sheets.get(file.name)
            if sheet_name:
                df = load_excel_sheet(file, sheet_name)
                if df is not None:
                    dfs.append(df)
        else:
            df = read_csv(file)
            if df is not None:
                dfs.append(df)
 
    if dfs and validate_columns(dfs):
        return pd.concat(dfs, ignore_index=True)
    else:
        st.error("Column mismatch detected. Ensure all files have the same structure.")
        return None
 
def preview_dataframe(df, n=5):
    """Preview the first few rows of a dataframe."""
    return df.head(n)
 
def summarize_csv_files(df, selected_operation, selected_columns, group_by_columns, include_all_columns=False):
    """Summarize data using the selected operation."""
    try:
        if not group_by_columns:
            st.warning("No grouping columns selected.")
            return pd.DataFrame()
 
        grouped = df.groupby(group_by_columns)
        results = {}
 
        for col in selected_columns:
            if selected_operation == "Min":
                results[col] = grouped[col].min()
            elif selected_operation == "Max":
                results[col] = grouped[col].max()
            elif selected_operation == "Sum":
                results[col] = grouped[col].sum()
            elif selected_operation == "Count":
                results[col] = grouped[col].count()
            elif selected_operation == "Average":
                results[col] = grouped[col].mean()
            elif selected_operation == "Median":
                results[col] = grouped[col].median()
            elif selected_operation == "Standard Deviation":
                results[col] = grouped[col].std()
 
        summary_df = pd.concat(results, axis=1).reset_index()
 
        if include_all_columns:
            extra_cols = [col for col in df.columns if col not in selected_columns + group_by_columns]
            for col in extra_cols:
                summary_df[col] = grouped[col].first().values
 
        return summary_df
 
    except Exception as e:
        st.error(f"Error during summarization: {e}")
        return pd.DataFrame()
 
# Streamlit UI - Page Title
st.markdown(
    """
    <div style="background-color:#94e399;padding:15px;border-radius:10px;text-align:center;font-size:30px;">
    📑 File Operations Tool
    </div>
    """,
    unsafe_allow_html=True
)
 
# User chooses an operation
operation = st.radio("**Choose an operation:**", ["Append Files", "Summarize Data", "P-C and C-P"])
 
# Global variable to store appended data
if "combined_df" not in st.session_state:
    st.session_state.combined_df = None
 
# Append Files Section
if operation == "Append Files":
    st.subheader("📁 Append multiple files")
    uploaded_files = st.file_uploader("Upload files (CSV/XLSX/XLS)", type=["csv", "xlsx", "xls"], accept_multiple_files=True)
 
    selected_sheets = {}
   
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith(("xlsx", "xls")):
                sheet_names = read_excel(file)
                if sheet_names and len(sheet_names) > 1:
                    selected_sheets[file.name] = st.selectbox(f"**Select a sheet for** {file.name}:", options=sheet_names)
                elif sheet_names:
                    selected_sheets[file.name] = sheet_names[0]
 
    if st.button("Append Files") and uploaded_files:
        st.session_state.combined_df = append_files(uploaded_files, selected_sheets)
 
        if st.session_state.combined_df is not None:
            st.write("### Preview of Combined Data")
            st.dataframe(preview_dataframe(st.session_state.combined_df))
           
            output_filename = "combined_data.csv"
            output_csv_path = os.path.join(TEMP_DIR, output_filename)
            st.session_state.combined_df.to_csv(output_csv_path, index=False)
 
            with open(output_csv_path, "rb") as f:
                st.download_button("Download Combined File", data=f, file_name=output_filename, mime="text/csv")
 
# Summarize Data Section
elif operation == "Summarize Data":
    st.subheader("📊 Summarize Data")
 
    df = None  # Ensure df is initialized
 
    col1, col2 = st.columns([1, 2])  # Left: Upload & Config, Right: Data Preview & Summary
 
    with col1:
        # Checkbox to use combined file
        use_combined = st.checkbox("Use Combined File from 'Append Files' Step", value=False)
 
        if use_combined and st.session_state.combined_df is not None:
            df = st.session_state.combined_df
        else:
            file = st.file_uploader("Upload a new file (CSV/XLSX/XLS)", type=["csv", "xlsx", "xls"])
            if file:
                if file.name.endswith(".csv"):
                    df = read_csv(file)
                else:
                    sheet_names = read_excel(file)
                    if sheet_names:
                        sheet_name = st.selectbox("Select a sheet:", options=sheet_names)
                        df = load_excel_sheet(file, sheet_name)
 
    if df is not None:
        with col2:
            st.write("### 📋 Data Preview")
            st.dataframe(preview_dataframe(df))
 
        with col1:
            numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
            all_columns = df.columns.tolist()
 
            group_by_columns = st.multiselect("Select columns to group by:", all_columns)
            selected_columns = st.multiselect("Select numeric columns to summarize:", numeric_columns)
            selected_operation = st.selectbox("Select summarization operation:", ["Min", "Max", "Sum", "Count", "Average", "Median", "Standard Deviation"])
            include_all_columns = st.checkbox("Include All Columns", value=False)
 
        with col2:
            if st.button("Summarize Data"):
                summary_results = summarize_csv_files(df, selected_operation, selected_columns, group_by_columns, include_all_columns)
               
                st.write("### 📊 Summarized Data")
                st.dataframe(summary_results)
 
                if not summary_results.empty:
                    csv = summary_results.to_csv(index=False).encode("utf-8")
                    st.download_button("Download Summary", csv, "summary_results.csv", "text/csv")

#P-C Section
elif operation == "P-C and C-P":
    with st.sidebar:
        st.markdown("<h3 class='step-header'>Step 1: Upload Files</h3>", unsafe_allow_html=True)
        premium_file = st.file_uploader("Upload Primary File", type=["csv", "xlsx"])
        commission_file = st.file_uploader("Upload Secondary File", type=["csv", "xlsx"])

    if premium_file and commission_file:
        premium_df = pd.read_csv(premium_file, encoding="ISO-8859-1") if premium_file.name.endswith(".csv") else pd.read_excel(premium_file)
        commission_df = pd.read_csv(commission_file, encoding="ISO-8859-1") if commission_file.name.endswith(".csv") else pd.read_excel(commission_file)

        # Step 2: Preview the uploaded files one below the other
        st.markdown("<h3 class='step-header'>Step 2: Preview Uploaded Files</h3>", unsafe_allow_html=True)

        # Primary File Preview
        st.subheader("Primary File Preview")
        st.dataframe(premium_df, height=200, use_container_width=True)  # Scrollbar enabled
        st.write(f"**Rows:** {premium_df.shape[0]}, **Columns:** {premium_df.shape[1]}")

        # Secondary File Preview
        st.subheader("Secondary File Preview")
        st.dataframe(commission_df, height=200, use_container_width=True)  # Scrollbar enabled
        st.write(f"**Rows:** {commission_df.shape[0]}, **Columns:** {commission_df.shape[1]}")

        # Step 3: Check for Unique Identifier
        common_columns = list(set(premium_df.columns) & set(commission_df.columns))
        st.markdown("<h3 class='step-header'>Step 3: Select Unique Identifier</h3>", unsafe_allow_html=True)
        
        if not common_columns:
            st.error("No key column present, Please choose another file.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                premium_identifier = st.selectbox("Select Identifier from Primary File", premium_df.columns)
            with col2:
                commission_identifier = st.selectbox("Select Identifier from Secondary File", commission_df.columns)

            # Step 4: Choose Operation
            st.markdown("<h3 class='step-header'>Step 4: Choose Operation</h3>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)  # Buttons aligned in a single row
            results_placeholder = st.container()  # Ensures the preview updates dynamically

            with col1:
                if st.button("Exact Matches"):
                    exact_matches = premium_df.merge(commission_df[[commission_identifier]], left_on=premium_identifier, right_on=commission_identifier, how='inner')
                    exact_matches = exact_matches[premium_df.columns]  # Keep only primary table columns
                    row_count, col_count = exact_matches.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 5: Exact Matches</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count}, **Columns:** {col_count}")
                        st.dataframe(exact_matches, height=400, use_container_width=True)
                        st.download_button("Download Exact Matches", convert_df_to_excel(exact_matches), "exact_matches.csv", "text/csv")

            with col2:
                if st.button("Records only in Primary"):
                    premium_only = premium_df.merge(commission_df[[commission_identifier]], left_on=premium_identifier, right_on=commission_identifier, how='left', indicator=True)
                    premium_only = premium_only[premium_only['_merge'] == 'left_only'].drop(columns=['_merge'])
                    row_count_p, col_count_p = premium_only.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 5: Records Only in Primary</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count_p}, **Columns:** {col_count_p}")
                        st.dataframe(premium_only, height=400, use_container_width=True)
                        st.download_button("Download Primary-Only Records", convert_df_to_excel(premium_only), "primary_only.csv", "text/csv")

            with col3:
                if st.button("Records only in Secondary"):
                    commission_only = commission_df.merge(premium_df[[premium_identifier]], left_on=commission_identifier, right_on=premium_identifier, how='left', indicator=True)
                    commission_only = commission_only[commission_only['_merge'] == 'left_only'].drop(columns=['_merge'])
                    commission_only = commission_only[commission_df.columns]  # Keep only secondary table columns
                    row_count_s, col_count_s = commission_only.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 5: Records Only in Secondary</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count_s}, **Columns:** {col_count_s}")
                        st.dataframe(commission_only, height=400, use_container_width=True)
                        st.download_button("Download Secondary-Only Records", convert_df_to_excel(commission_only), "secondary_only.csv", "text/csv")
