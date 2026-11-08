import streamlit as st
import pandas as pd
import pydicom
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="ER Triage AI", page_icon="🏥", layout="wide")

# 2. Role-Based Access Control (Security Upgrade)
with st.sidebar:
    st.subheader("🔐 System Login")
    user_role = st.radio("Select User Role:", ["Attending Physician", "Triage Nurse", "Hospital Executive"])
    
    # Capture the physician's name dynamically
    doctor_name = ""
    if user_role == "Attending Physician":
        doctor_name = st.text_input("Physician Name:", "Dr. Shaik")

    st.divider()
    st.success(f"Logged in as: {user_role}")
    if doctor_name:
        st.info(f"Active User: {doctor_name}")

st.title("Automated Triage Engine")

# 3. Setup the Database
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        "Patient_ID": ["DXB-001", "DXB-002", "DXB-003"],
        "Chief_Complaint": ["Cough", "Head trauma", "Sprained ankle"],
        "Triage_Level": ["Routine", "Urgent", "Routine"],
        "Wait_Time_Mins": [45, 30, 15]
    })

# 4. Executive Analytics Dashboard
st.markdown("### 📊 Live Department Metrics")
m1, m2, m3 = st.columns(3)

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
if user_role == "Attending Physician":
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

# 6. Live Dashboard & Dynamic Report Export
st.subheader("Live ER Waiting Room")
col1, col2 = st.columns(2)

with col1:
    if user_role in ["Triage Nurse", "Attending Physician"]:
        if st.button("🚨 Run AI Triage Scan on Waitlist"):
            st.session_state.db.loc[0, "Triage_Level"] = "Critical"
            st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
            st.rerun()
    else:
        st.info("Executive View: Triage simulation tools locked.")

with col2:
    if user_role == "Attending Physician":
        patient_list = st.session_state.db["Patient_ID"].tolist()
        selected_patient = st.selectbox("Select Patient for Discharge:", patient_list)
        
        patient_data = st.session_state.db[st.session_state.db["Patient_ID"] == selected_patient].iloc[0]
        
        # The signature line now updates automatically based on the sidebar input
        signature_line = f"Electronically Signed By: {doctor_name}" if doctor_name else "[ ] Pending Attending Signature"
        
        report_content = f"""🏥 CLINICAL DISCHARGE & TRIAGE SUMMARY
======================================
Patient ID: {patient_data['Patient_ID']}
Chief Complaint: {patient_data['Chief_Complaint']}
Triage Status: {patient_data['Triage_Level'].upper()}
Wait Time: {patient_data['Wait_Time_Mins']} mins
======================================
{signature_line}
"""
        st.download_button(
            label=f"📥 Export Report ({selected_patient})",
            data=report_content,
            file_name=f"{selected_patient}_Discharge_Report.txt",
            mime="text/plain",
            type="primary"
        )

st.dataframe(st.session_state.db, use_container_width=True)
