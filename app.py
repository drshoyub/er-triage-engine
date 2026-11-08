import streamlit as st
import pandas as pd

# 1. Page Configuration (The Web App Tab)
st.set_page_config(page_title="ER Triage AI", page_icon="🏥")
st.title("Automated Radiology Triage Engine")

# 2. Setup the Database
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        "Patient_ID": ["DXB-001", "DXB-002", "DXB-003"],
        "Chief_Complaint": ["Cough", "Head trauma", "Sprained ankle"],
        "Triage_Level": ["Routine", "Urgent", "Routine"],
        "Wait_Time_Mins": [45, 30, 15]
    })

# 3. Create the UI Layout (Columns and Buttons)
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Run AI Triage Scan"):
        st.warning("AI detected high-risk anomaly in DXB-001. Updating queue...")
        st.session_state.db.loc[0, "Triage_Level"] = "Critical"
        st.session_state.db = st.session_state.db.sort_values(by="Triage_Level")

with col2:
    if st.button("📄 Auto-Draft Discharge"):
        st.info("Generating standard discharge report for DXB-001...")
        st.code("Diagnosis: Acute Pneumonia. \nPlan: Pulmonology Consult.")

# 4. Display the Live Dashboard
st.subheader("Live ER Waiting Room")
st.dataframe(st.session_state.db, use_container_width=True)