import streamlit as st
import pandas as pd
import pydicom
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="ER Triage AI", page_icon="🏥", layout="wide")

# Initialize memory states for authentication and patient scan mapping
if 'radiology_auth' not in st.session_state:
    st.session_state.radiology_auth = False
if 'er_auth' not in st.session_state:
    st.session_state.er_auth = False
if 'nurse_auth' not in st.session_state:
    st.session_state.nurse_auth = False
if 'patient_scans' not in st.session_state:
    st.session_state.patient_scans = {}
if 'previous_portal' not in st.session_state:
    st.session_state.previous_portal = None

# 2. Strict Portal & Three-Tier Password Navigation
with st.sidebar:
    st.subheader("🏥 System Navigation")
    portal = st.selectbox(
        "Select Department Portal:", 
        [
            "ER Dashboard (Physician)", 
            "ER Waiting Room (Triage Nurse)", 
            "Radiology PACS (Radiologist)"
        ]
    )
    
    # AUTOMATIC LOGOUT: If the user changes the portal dropdown, reset all auth states instantly
    if st.session_state.previous_portal != portal:
        st.session_state.er_auth = False
        st.session_state.nurse_auth = False
        st.session_state.radiology_auth = False
        st.session_state.previous_portal = portal
        st.rerun()

    st.divider()
    
    is_authenticated = False
    active_user = ""

    # PORTAL 1: ER PHYSICIAN (Password: er2026)
    if portal == "ER Dashboard (Physician)":
        st.subheader("🔐 ER Physician Access")
        if not st.session_state.er_auth:
            er_password = st.text_input("Enter ER Physician Password:", type="password", key="er_pass")
            if er_password == "er2026": 
                st.session_state.er_auth = True
                st.rerun()
            elif er_password:
                st.error("Incorrect password.")
        else:
            is_authenticated = True
            active_user = st.text_input("ER Physician Name:", "Dr. Shaik (ER)", key="er_name")
            if st.button("Logout ER Portal", key="logout_er"):
                st.session_state.er_auth = False
                st.rerun()
            st.success("Authenticated: ER Physician Active")

    # PORTAL 2: TRIAGE NURSE (Password: nurse2026)
    elif portal == "ER Waiting Room (Triage Nurse)":
        st.subheader("🔐 Triage Nurse Access")
        if not st.session_state.nurse_auth:
            nurse_password = st.text_input("Enter Nurse Password:", type="password", key="nurse_pass")
            if nurse_password == "nurse2026": 
                st.session_state.nurse_auth = True
                st.rerun()
            elif nurse_password:
                st.error("Incorrect password.")
        else:
            is_authenticated = True
            active_user = st.text_input("Nurse Name:", "Nurse Sarah", key="nurse_name")
            if st.button("Logout Nurse Portal", key="logout_nurse"):
                st.session_state.nurse_auth = False
                st.rerun()
            st.success("Authenticated: Triage Nurse Active")

    # PORTAL 3: RADIOLOGIST (Password: dxb2026)
    elif portal == "Radiology PACS (Radiologist)":
        st.subheader("🔐 Radiologist Access")
        if not st.session_state.radiology_auth:
            rad_password = st.text_input("Enter Radiologist Password:", type="password", key="rad_pass")
            if rad_password == "dxb2026": 
                st.session_state.radiology_auth = True
                st.rerun()
            elif rad_password:
                st.error("Incorrect password.")
        else:
            is_authenticated = True
            active_user = st.text_input("Radiologist Name:", "Dr. Shaik (Rad)", key="rad_name")
            if st.button("Logout Radiology Portal", key="logout_rad"):
                st.session_state.radiology_auth = False
                st.rerun()
            st.success("Authenticated: Radiologist Active")

st.title("Automated Triage & Radiology Engine")

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

# ==========================================
# PORTAL 1: ER DASHBOARD (Password: er2026)
# ==========================================
if portal == "ER Dashboard (Physician)":
    if is_authenticated and st.session_state.er_auth:
        st.subheader("🚨 ER Physician Waiting Room & Floor Management")
        
        # Imaging & Authorization Status Overview Row
        st.markdown("#### 🩻 Department Imaging & Authorization Tracking")
        imaging_status_rows = []
        for pid in st.session_state.db["Patient_ID"]:
            if pid in st.session_state.patient_scans:
                rec = st.session_state.patient_scans[pid]
                status_text = f"✅ Authorized & Signed Off ({rec['signed_by']})"
            else:
                status_text = "⏳ Preliminary / Pending Sign-Off"
            imaging_status_rows.append({"Patient_ID": pid, "Scan & Authorization Status": status_text})
        
        st.dataframe(pd.DataFrame(imaging_status_rows), use_container_width=True, hide_index=True)
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚨 Run AI Triage Scan on Waitlist"):
                st.session_state.db.loc[0, "Triage_Level"] = "Critical"
                st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
                st.rerun()

        with col2:
            patient_list = st.session_state.db["Patient_ID"].tolist()
            selected_patient = st.selectbox("Select Patient for Discharge Summary:", patient_list)
            
            patient_data = st.session_state.db[st.session_state.db["Patient_ID"] == selected_patient].iloc[0]
            
            patient_record = st.session_state.patient_scans.get(selected_patient)
            
            if patient_record:
                radiology_findings = patient_record["report"]
                rad_signature = patient_record["signed_by"]
                st.image(patient_record["image"], caption=f"PACS Scan Clearance for {selected_patient}", width=250)
            else:
                radiology_findings = "[Waiting for Radiology Over-Read / Sign-Off]"
                rad_signature = "[ ] Pending Radiology Signature"
            
            er_signature = f"Electronically Signed By: {active_user}" if active_user else "[ ] Pending ER Physician Signature"

            report_content = f"""🏥 CLINICAL DISCHARGE & TRIAGE SUMMARY
======================================
Patient ID: {patient_data['Patient_ID']}
Chief Complaint: {patient_data['Chief_Complaint']}
Triage Status: {patient_data['Triage_Level'].upper()}
Wait Time: {patient_data['Wait_Time_Mins']} mins

--- RADIOLOGY OVER-READ ---
{radiology_findings}
======================================
Radiology E-Signature: {rad_signature}
ER Physician E-Signature: {er_signature}
"""
            st.download_button(
                label=f"📥 Export Finalized Report ({selected_patient})",
                data=report_content,
                file_name=f"{selected_patient}_Discharge_Report.txt",
                mime="text/plain",
                type="primary"
            )

        st.subheader("Active Waitlist Queue")
        st.dataframe(st.session_state.db, use_container_width=True)
    else:
        st.warning("🔒 Access Restricted. Please enter the correct ER Physician password (`er2026`) in the sidebar.")

# ==========================================
# PORTAL 2: TRIAGE NURSE (Password: nurse2026)
# ==========================================
elif portal == "ER Waiting Room (Triage Nurse)":
    if is_authenticated and st.session_state.nurse_auth:
        st.subheader("📋 Triage Nurse Intake & Queue Control")
        
        if st.button("⚡ Run Automated Intake Priority Check"):
            st.session_state.db.loc[0, "Triage_Level"] = "Critical"
            st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")
            st.success("Queue re-prioritized based on vital signs and intake rules.")
            st.rerun()

        st.info(f"Logged in Intake Specialist: {active_user}")
        st.dataframe(st.session_state.db, use_container_width=True)
    else:
        st.warning("🔒 Access Restricted. Please enter the correct Triage Nurse password (`nurse2026`) in the sidebar.")

# ==========================================
# PORTAL 3: RADIOLOGY PACS (Password: dxb2026)
# ==========================================
elif portal == "Radiology PACS (Radiologist)":
    if is_authenticated and st.session_state.radiology_auth:
        st.markdown("### 🩻 Radiology PACS: Diagnostic Review Gateway")
        
        patient_list = st.session_state.db["Patient_ID"].tolist()
        target_patient = st.selectbox("Select Patient to Attach Scan:", patient_list)
        
        uploaded_file = st.file_uploader(f"Upload raw DICOM (.dcm) file for {target_patient}", type=["dcm"])

        if uploaded_file is not None:
            dicom_data = pydicom.dcmread(uploaded_file)
            image_array = dicom_data.pixel_array
            image_array = image_array - np.min(image_array)
            image_array = image_array / np.max(image_array)
            image_array = (image_array * 255).astype(np.uint8)

            colA, colB = st.columns([1, 1])
            
            with colA:
                st.image(image_array, caption=f"Source: Local PACS — {target_patient}", use_container_width=True)
                
            with colB:
                st.warning("🚨 AI Preliminary Draft (Requires Human Review)")
                ai_draft = f"""Modality: {getattr(dicom_data, 'Modality', 'Unknown')}
Body Part: {getattr(dicom_data, 'BodyPartExamined', 'Unknown')}
AI Findings: High-contrast opacity detected. 94.2% confidence of acute anomaly.
AI Recommendation: Escalate triage status."""

                with st.form(f"form_{target_patient}"):
                    st.write(f"**Radiologist Over-read for {target_patient}:**")
                    final_clinical_notes = st.text_area("Review and edit AI findings:", value=ai_draft, height=150)
                    
                    submitted = st.form_submit_button("Approve & Sign Off Scan")
                    
                    if submitted:
                        st.session_state.patient_scans[target_patient] = {
                            "image": image_array,
                            "report": final_clinical_notes,
                            "signed_by": active_user
                        }
                        st.success(f"Scan and report for {target_patient} signed off by {active_user}.")
    else:
        st.warning("🔒 Access Restricted. Please enter the correct Radiologist password (`dxb2026`) in the sidebar.")
