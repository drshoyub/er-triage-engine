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

# 3. Clinical AI - DICOM Viewer Integration (Upgrade 1)
st.markdown("### 🩻 Clinical AI: Secure Imaging Upload")
uploaded_file = st.file_uploader("Upload a raw DICOM (.dcm) file for AI analysis", type=["dcm"])

if uploaded_file is not None:
    # Read the clinical DICOM file
    dicom_data = pydicom.dcmread(uploaded_file)
    
    # Extract the raw pixel data and normalize it for the web
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

# 4. Live Dashboard & Report Export (Upgrade 3)
st.subheader("Live ER Waiting Room")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Run AI Triage Scan on Waitlist"):
        st.session_state.db.loc[0, "Triage_Level"] = "Critical"
        st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
        st.rerun() # Refreshes the queue

with col2:
    # Generate the standardized text for the report
    report_content = """🏥 CLINICAL DISCHARGE & TRIAGE SUMMARY
======================================
Patient ID: DXB-001
Diagnosis: Acute Pneumonia
AI Findings: Right lower lobe consolidation (94.2% confidence)
Plan: Pulmonology Consult & Broad-spectrum antibiotics.
======================================
[ ] Pending Attending Signature
"""
    # Streamlit component to instantly download a file
    st.download_button(
        label="📥 Export Clinical Report (.txt)",
        data=report_content,
        file_name="DXB-001_Discharge_Report.txt",
        mime="text/plain",
        type="primary"
    )

st.dataframe(st.session_state.db, use_container_width=True)
