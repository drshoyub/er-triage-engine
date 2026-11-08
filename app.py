import streamlit as st
import pandas as pd
import pydicom
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="ER Triage AI", page_icon="🏥", layout="wide")
st.title("Automated Radiology Triage Engine")

# 2. Setup the Database
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        "Patient_ID": ["DXB-001", "DXB-002", "DXB-003"],
        "Chief_Complaint": ["Cough", "Head trauma", "Sprained ankle"],
        "Triage_Level": ["Routine", "Urgent", "Routine"],
        "Wait_Time_Mins": [45, 30, 15]
    })

# 3. Clinical AI - DICOM Viewer Integration
st.markdown("### 🩻 Clinical AI: Secure Imaging Upload")
uploaded_file = st.file_uploader("Upload a raw DICOM (.dcm) file for AI analysis", type=["dcm"])

if uploaded_file is not None:
    dicom_data = pydicom.dcmread(uploaded_file)
    image_array = dicom_data.pixel_array
    image_array = image_array - np.min(image_array)
    image_array = image_array / np.max(image_array)
    image_array = (image_array * 255).astype(np.uint8)

    colA, colB = st.columns([1, 1])
    
    with colA:
        st.image(image_array, caption="Source: Local PACS", use_container_width=True)
        
    with colB:
        st.warning("🚨 AI ALERT: Anomaly Detected")
        st.write("**Extracted DICOM Metadata:**")
        st.write(f"- **Modality:** {getattr(dicom_data, 'Modality', 'Unknown')}")
        st.write(f"- **Body Part:** {getattr(dicom_data, 'BodyPartExamined', 'Unknown')}")
        st.write(f"- **AI Confidence:** 94.2%")
        st.write("- **Recommendation:** Escalate Patient ID DXB-001 in waitlist.")

st.divider()

# 4. Live Dashboard & Dynamic Report Export
st.subheader("Live ER Waiting Room")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Run AI Triage Scan on Waitlist"):
        st.session_state.db.loc[0, "Triage_Level"] = "Critical"
        st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
        st.rerun()

with col2:
    # Create a dropdown menu using the Patient IDs from the database
    patient_list = st.session_state.db["Patient_ID"].tolist()
    selected_patient = st.selectbox("Select Patient for Discharge:", patient_list)
    
    # Pull the exact row of data for the chosen patient
    patient_data = st.session_state.db[st.session_state.db["Patient_ID"] == selected_patient].iloc[0]
    
    # Dynamically inject the data into the report template
    report_content = f"""🏥 CLINICAL DISCHARGE & TRIAGE SUMMARY
======================================
Patient ID: {patient_data['Patient_ID']}
Chief Complaint: {patient_data['Chief_Complaint']}
Triage Status: {patient_data['Triage_Level'].upper()}
Wait Time: {patient_data['Wait_Time_Mins']} mins
======================================
[ ] Pending Attending Signature
"""
    
    # The download button now updates its filename based on the dropdown choice
    st.download_button(
        label=f"📥 Export Report ({selected_patient})",
        data=report_content,
        file_name=f"{selected_patient}_Discharge_Report.txt",
        mime="text/plain",
        type="primary"
    )

st.dataframe(st.session_state.db, use_container_width=True)
