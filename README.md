# File_Matching_Tool
Here's a concise **README** for your project:  

---

# 📊 P-C and C-P Tool  

## Overview  
The **P-C and C-P Tool** is a Streamlit-based application that compares two datasets (Primary and Secondary) based on a unique identifier. It allows users to:  
✔ Find **exact matches** while prioritizing primary file columns.  
✔ Identify **records present only in the primary file** (keeping only primary file columns).  
✔ Identify **records present only in the secondary file** (keeping only secondary file columns).  

## Features  
- **Upload Files**: Supports CSV and Excel formats.  
- **Custom Column Matching**: Users can select the unique identifier for comparison.  
- **Flexible Filtering**: Choose from **Exact Matches, Primary-Only, or Secondary-Only** records.  
- **Download Results**: Export filtered data in Excel format.  

## How to Use  
1. Upload the **Primary** and **Secondary** files.  
2. Select the **unique identifier** for comparison.  
3. Choose an operation:  
   - **Exact Matches** → Retains all columns but prioritizes the primary file's values.  
   - **Records only in Primary** → Keeps only primary file columns.  
   - **Records only in Secondary** → Keeps only secondary file columns.  
4. Preview the results and download the processed file.  

## Requirements  
- Python 3.x  
- Libraries: `streamlit`, `pandas`, `xlsxwriter`  

## Installation  
```bash
pip install streamlit pandas xlsxwriter
```

## Run the App  
```bash
streamlit run joins5.py   #join5 is the main app file
```

