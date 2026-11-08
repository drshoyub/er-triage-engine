import streamlit as st
import pandas as pd
import pydicom
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="ER Triage AI", page_icon="🏥", layout="wide")

# 2. Role-Based Access Control (Security Upgrade)
with st.sidebar:
    st.subheader("🔐 System Login")
    # This radio button simulates different hospital staff logging in
    user_role = st.radio("Select User Role:", ["Attending Physician", "Triage Nurse", "Hospital Executive"])
    st.divider()
    st.success(f"Logged in as: {user_role}")
    st.caption("DHA Law No. 11: Local Processing ACTIVE")

st.title("Automated Radiology Triage Engine")

# 3. Setup the Database
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        "Patient_ID": ["DXB-001", "DXB-002", "DXB-003"],
        "Chief_Complaint": ["Cough", "Head trauma", "Sprained ankle"],
        "Triage_Level": ["Routine", "Urgent", "Routine"],
        "Wait_Time_Mins": [45, 30, 15]
    })

# 4. Executive Analytics Dashboard (Business Upgrade)
st.markdown("### 📊 Live Department Metrics")
m1, m2, m3 = st.columns(3)

# Calculate live metrics directly from the Pandas dataframe
avg_wait = int(st.session_state.db["Wait_Time_Mins"].mean())
critical_count = len(st.session_state.db[st.session_state.db["Triage_Level"] == "Critical"])

with m1:
    st.metric(label="Patients in Queue", value=len(st.session_state.db))
with m2:
    st.metric(label="Average Wait Time", value=f"{avg_wait} mins", delta="-12 mins (vs last week)")
with m3:
    st.metric(label="Critical Patients", value=critical_count, delta=critical_count, delta_color="inverse")

st.divider()

# 5. Clinical AI - DICOM Viewer (Restricted Access)
# The image uploader is now completely hidden unless a doctor is logged in
if user_role == "Attending Physician":
    st.markdown("### 🩻 Clinical AI: Secure Imaging Upload")
    uploaded_file = st.file_uploader("Upload a raw DICOM (.dcm) file for AI analysis", type=["dcm"])

    if uploaded_file is not None:
        dicom_data = pydicom.dcmread(uploaded_file)
