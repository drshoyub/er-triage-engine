import streamlit as st
import pandas as pd
import pydicom
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="ER Triage AI", page_icon="🏥", layout="wide")

# Initialize memory states for authentication and clinical workflow
if 'physician_auth' not in st.session_state:
    st.session_state.physician_auth = False
if 'signed_off_report' not in st.session_state:
    st.session_state.signed_off_report = None
if 'report_signed_by' not in st.session_state:
    st.session_state.report_signed_by = ""

# 2. Department Navigation & Separated Logins
with st.sidebar:
    st.subheader("🏥 Department Navigation")
    portal = st.radio("Select Portal:", ["ER Dashboard", "Radiology Portal (PACS)"])
    st.divider()
    
    user_role = ""
    doctor_name = ""
    is_authenticated = False

    # RADIOLOGY LOGIN (Isolated)
    if portal == "Radiology Portal (PACS)":
        st.subheader("🔐 Radiologist Login")
        if not st.session_state.physician_auth:
            password = st.text_input("Enter Radiologist Password:", type="password")
            if password == "dxb2026": 
                st.session_state.physician_auth = True
                st.rerun()
            elif password:
                st.error("Incorrect password.")
        else:
            is_authenticated = True
            user_role = "Radiologist"
            doctor_name = st.text_input("Radiologist Name:", "Dr. Shaik")
            if st.button("Logout"):
                st.session_state.physician_auth = False
                st.rerun()
            st.success("Authentication successful.")

    # ER DASHBOARD LOGIN
    elif portal == "ER Dashboard":
        st.subheader("👤 ER Staff Login")
        user_role = st.radio("Select ER Role:", ["Triage Nurse", "Hospital Executive"])
        is_authenticated = True 
        st.success(f"Active Role: {user_role}")

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

# 5. RADIOLOGY PORTAL VIEW
if portal == "Radiology Portal (PACS)":
    if is_authenticated:
        st.markdown("### 🩻 Clinical AI: Diagnostic Review Gateway")
        uploaded_file = st.file_uploader("Upload a raw DICOM (.dcm) file for Patient DXB-001", type=["dcm"])

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
                st.warning("🚨 AI Preliminary Draft (Requires Human Review)")
                ai_draft = f"""Modality: {getattr(dicom_data, 'Modality', 'Unknown')}
Body Part: {getattr(dicom_data, 'BodyPartExamined', 'Unknown')}
AI Findings: High-contrast opacity detected. 94.2% confidence of acute anomaly.
AI Recommendation: Escalate triage status."""

                with st.form("radiologist_signoff_form"):
                    st.write("**Radiologist Over-read:**")
                    final_clinical_notes = st.text_area("Review and edit AI findings before finalizing:", value=ai_draft, height=150)
                    
                    submitted = st.form_submit_button("Approve & Sign Off Document")
                    
                    if submitted:
                        st.session_state.signed_off_report = final_clinical_notes
                        st.session_state.report_signed_by = doctor_name
                        st.success(f"Report officially signed off by {doctor_name}. Transmitted to ER.")
    else:
        st.warning("Please enter your password in the sidebar to securely access clinical imaging tools.")

# 6. ER DASHBOARD VIEW
elif portal == "ER Dashboard":
    st.subheader("Live ER Waiting Room")
    col1, col2 = st.columns(2)

    with col1:
        if user_role == "Triage Nurse":
            if st.button("🚨 Run AI Triage Scan on Waitlist"):
                st.session_state.db.loc[0, "Triage_Level"] = "Critical"
                st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
                st.rerun()
        else:
            st.info("Executive View: Triage simulation tools locked.")

    with col2:
        if user_role == "Triage Nurse":
            patient_list = st.session_state.db["Patient_ID"].tolist()
            selected_patient = st.selectbox("Select Patient for Discharge:", patient_list)
            
            patient_data = st.session_state.db[st.session_state.db["Patient_ID"] == selected_patient].iloc[0]
            
            radiology_findings = st.session_state.signed_off_report if st.session_state.signed_off_report else "[No Imaging Signed Off]"
            signature = st.session_state.report_signed_by if st.session_state.report_signed_by else "[ ] Pending Signature"
            
            report_content = f"""🏥 CLINICAL DISCHARGE & TRIAGE SUMMARY
======================================
Patient ID: {patient_data['Patient_ID']}
Chief Complaint: {patient_data['Chief_Complaint']}
Triage Status: {patient_data['Triage_Level'].upper()}
Wait Time: {patient_data['Wait_Time_Mins']} mins

--- RADIOLOGY OVER-READ ---
{radiology_findings}
======================================
Radiology E-Signature: {signature}
Discharging Nurse: [Pending]
"""
            st.download_button(
                label=f"📥 Export Finalized Report ({selected_patient})",
                data=report_content,
                file_name=f"{selected_patient}_Discharge_Report.txt",
                mime="text/plain",
                type="primary"
            )

    st.dataframe(st.session_state.db, use_container_width=True)
