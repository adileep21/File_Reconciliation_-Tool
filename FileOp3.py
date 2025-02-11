import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Set Streamlit page configuration
st.set_page_config(
    page_title="📑 File Operations Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure a temporary directory exists
TEMP_DIR = "temp_uploaded_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Apply Custom CSS for Styling
st.markdown("""
    <style>
        .main-title {
            background-color: #c8e6c9;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
        }
        .step-header {
            font-size: 18px;
            font-weight: bold;
            color: #2E7D32;
            text-align: left;
            margin-bottom: 5px;
        }
        .stButton > button {
            width: 100%;
            font-size: 14px;
            padding: 6px;
            height: 40px;
        }
        .stDataFrame {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Function to Convert DataFrame to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Cache data to improve speed
@st.cache_data(show_spinner=False)
def read_csv(file):
    try:
        return pd.read_csv(file, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

@st.cache_data(show_spinner=False)
def read_excel(file):
    try:
        excel_file = pd.ExcelFile(file, engine="openpyxl")
        return excel_file.sheet_names
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

def load_excel_sheet(file, sheet_name):
    try:
        return pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading sheet '{sheet_name}': {e}")
        return None

@st.cache_data(show_spinner=False)
def validate_columns(dfs):
    columns_list = [set(df.columns) for df in dfs]
    return all(cols == columns_list[0] for cols in columns_list)

@st.cache_data(show_spinner=False)
def append_files(files, selected_sheets):
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
operation = st.radio("Choose an operation:", ["Append Files", "Summarize Data", "P-C and C-P"])

if operation == "Append Files":
    st.subheader("📁 Append multiple files into a single dataset")
    uploaded_files = st.file_uploader("Upload files (CSV/XLSX/XLS)", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

    selected_sheets = {}
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith(("xlsx", "xls")):
                sheet_names = read_excel(file)
                if sheet_names and len(sheet_names) > 1:
                    selected_sheets[file.name] = st.selectbox(f"Select a sheet for {file.name}:", options=sheet_names)
                elif sheet_names:
                    selected_sheets[file.name] = sheet_names[0]

    if st.button("Append Files") and uploaded_files:
        combined_df = append_files(uploaded_files, selected_sheets)
        if combined_df is not None:
            st.dataframe(combined_df)
            st.download_button("Download Combined File", convert_df_to_excel(combined_df), "combined_data.xlsx")

elif operation == "Summarize Data":
    st.subheader("📊 Summarize Data")
    file = st.file_uploader("Upload a CSV/XLSX file", type=["csv", "xlsx", "xls"])
    if file:
        df = read_csv(file) if file.name.endswith(".csv") else load_excel_sheet(file, read_excel(file)[0])
        if df is not None:
            st.dataframe(df.head())
            group_by_columns = st.multiselect("Select columns to group by", df.columns)
            numeric_columns = df.select_dtypes(include="number").columns.tolist()
            selected_columns = st.multiselect("Select numeric columns to summarize", numeric_columns)
            operation = st.selectbox("Choose an operation", ["Sum", "Mean", "Median", "Min", "Max", "Count"])
            if st.button("Summarize"):
                summary_df = df.groupby(group_by_columns).agg({col: operation.lower() for col in selected_columns})
                st.dataframe(summary_df)
                st.download_button("Download Summary", convert_df_to_excel(summary_df), "summary_data.xlsx")

elif operation == "P-C and C-P":
    with st.sidebar:
        st.markdown("<h3 class='step-header'>Step 1: Upload Files</h3>", unsafe_allow_html=True)
        premium_file = st.file_uploader("Upload Primary File", type=["csv", "xlsx"])
        commission_file = st.file_uploader("Upload Secondary File", type=["csv", "xlsx"])

    if premium_file and commission_file:
        premium_df = pd.read_csv(premium_file,encoding="ISO-8859-1") if premium_file.name.endswith(".csv") else pd.read_excel(premium_file)
        commission_df = pd.read_csv(commission_file,encoding="ISO-8859-1") if commission_file.name.endswith(".csv") else pd.read_excel(commission_file)    

        # Step 2: Check for common columns
        common_columns = list(set(premium_df.columns) & set(commission_df.columns))
        st.markdown("<h3 class='step-header'>Step 2: Select Unique Identifier</h3>", unsafe_allow_html=True)
        if not common_columns:
            st.error("No key column present, Please choose another file.")
        else:
            col1, col2 = st.columns(2) 
            with col1:
                premium_identifier = st.selectbox("Select Identifier from Primary File", premium_df.columns)
            with col2:
                commission_identifier = st.selectbox("Select Identifier from Secondary File", commission_df.columns)    

            # Step 3: Choose Operation   
            st.markdown("<h3 class='step-header'>Step 3: Choose Operation</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)  # Buttons aligned in a single row
            results_placeholder = st.container()  # Ensures the preview updates dynamically

            with col1:
                if st.button("Exact Matches"):
                    exact_matches = premium_df.merge(commission_df[[commission_identifier]], left_on=premium_identifier, right_on=commission_identifier, how='inner')
                    exact_matches = exact_matches[premium_df.columns]  # Keep only primary table columns
                    row_count, col_count = exact_matches.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 4: Exact Matches</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count}, **Columns:** {col_count}")
                        st.dataframe(exact_matches, height=400, use_container_width=True)
                        st.download_button("Download Exact Matches", convert_df_to_excel(exact_matches), "exact_matches.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with col2:
                if st.button("Records only in Primary"):
                    premium_only = premium_df.merge(commission_df[[commission_identifier]], left_on=premium_identifier, right_on=commission_identifier, how='left', indicator=True)
                    premium_only = premium_only[premium_only['_merge'] == 'left_only'].drop(columns=['_merge'])
                    row_count_p, col_count_p = premium_only.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 4: Records Only in Primary</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count_p}, **Columns:** {col_count_p}")
                        st.dataframe(premium_only, height=400, use_container_width=True)
                        st.download_button("Download Primary-Only Records", convert_df_to_excel(premium_only), "primary_only.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with col3:
                if st.button("Records only in Secondary"):
                    commission_only = commission_df.merge(premium_df[[premium_identifier]], left_on=commission_identifier, right_on=premium_identifier, how='left', indicator=True)
                    commission_only = commission_only[commission_only['_merge'] == 'left_only'].drop(columns=['_merge'])
                    commission_only = commission_only[commission_df.columns]  # Keep only secondary table columns
                    row_count_s, col_count_s = commission_only.shape
                    with results_placeholder:
                        st.markdown("<h3 class='step-header'>Step 4: Records Only in Secondary</h3>", unsafe_allow_html=True)
                        st.write(f"**Rows:** {row_count_s}, **Columns:** {col_count_s}")
                        st.dataframe(commission_only, height=400, use_container_width=True)
                        st.download_button("Download Secondary-Only Records", convert_df_to_excel(commission_only), "secondary_only.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    