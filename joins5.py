import streamlit as st
import pandas as pd
from io import BytesIO

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

# Main Title
st.markdown("<div class='main-title'>Data Matching and Comparison Tool</div>", unsafe_allow_html=True)

# Sidebar - Step 1 and Step 2
with st.sidebar:
    st.markdown("<h3 class='step-header'>Step 1: Upload Files</h3>", unsafe_allow_html=True)
    premium_file = st.file_uploader("Upload Primary File", type=["csv", "xlsx"])
    commission_file = st.file_uploader("Upload Secondary File", type=["csv", "xlsx"])

    if premium_file and commission_file:
        premium_df = pd.read_csv(premium_file) if premium_file.name.endswith(".csv") else pd.read_excel(premium_file)
        commission_df = pd.read_csv(commission_file) if commission_file.name.endswith(".csv") else pd.read_excel(commission_file)

        st.markdown("<h3 class='step-header'>Step 2: Select Unique Identifier</h3>", unsafe_allow_html=True)
        premium_identifier = st.selectbox("Select Identifier from Primary File", premium_df.columns)
        commission_identifier = st.selectbox("Select Identifier from Secondary File", commission_df.columns)

# Step 3: Choose Operation
if premium_file and commission_file:
    st.markdown("<h3 class='step-header'>Step 3: Choose Operation</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)  # Buttons aligned in a single row
    results_placeholder = st.container()  # **This ensures the preview updates dynamically**

    with col1:
        if st.button("Exact Matches"):
            exact_matches = premium_df.merge(commission_df, left_on=premium_identifier, right_on=commission_identifier, how='inner')
            with results_placeholder:
                st.markdown("<h3 class='step-header'>Step 4: Exact Matches</h3>", unsafe_allow_html=True)
                st.dataframe(exact_matches, height=400, use_container_width=True)
                st.download_button("Download Exact Matches", convert_df_to_excel(exact_matches), "exact_matches.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col2:
        if st.button("Records only in Primary"):
            premium_only = premium_df.merge(commission_df, left_on=premium_identifier, right_on=commission_identifier, how='left', indicator=True)
            premium_only = premium_only[premium_only['_merge'] == 'left_only'].drop(columns=['_merge'])
            with results_placeholder:
                st.markdown("<h3 class='step-header'>Step 4: Records Only in Primary</h3>", unsafe_allow_html=True)
                st.dataframe(premium_only, height=400, use_container_width=True)
                st.download_button("Download Primary-Only Records", convert_df_to_excel(premium_only), "primary_only.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col3:
        if st.button("Records only in Secondary"):
            commission_only = commission_df.merge(premium_df, left_on=commission_identifier, right_on=premium_identifier, how='left', indicator=True)
            commission_only = commission_only[commission_only['_merge'] == 'left_only'].drop(columns=['_merge'])
            with results_placeholder:
                st.markdown("<h3 class='step-header'>Step 4: Records Only in Secondary</h3>", unsafe_allow_html=True)
                st.dataframe(commission_only, height=400, use_container_width=True)
                st.download_button("Download Secondary-Only Records", convert_df_to_excel(commission_only), "secondary_only.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
