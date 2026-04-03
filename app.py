import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓")

# --- GOOGLE SHEETS CONNECTION ---
# Paste your public Google Sheet link here
# Format: https://docs.google.com/spreadsheets/d/your-id-here/edit#gid=0
url = "https://docs.google.com/spreadsheets/d/1ann4DYVPMdo9kwXNfDq59WssQE49m-__l-uuYyc7Zck/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- DATA LOADING ---
def load_data():
    # Load Student List (Local CSV still works for the source list)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    students_path = os.path.join(current_dir, 'students.csv')
    all_students_df = pd.read_csv(students_path)
    all_students = all_students_df['Name'].tolist()

    # Load Existing Registrations from Google Sheets
    try:
        existing_data = conn.read(spreadsheet=url, usecols=[0,1,2,3,4])
        existing_data = existing_data.dropna(how="all")
        
        assigned_students = []
        for col in ['Member 1', 'Member 2', 'Member 3']:
            if col in existing_data.columns:
                assigned_students.extend(existing_data[col].dropna().tolist())
        return all_students, assigned_students, existing_data
    except:
        return all_students, [], pd.DataFrame()

supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
all_students, assigned_students, existing_data = load_data()

# --- THE FORM ---
st.title("🎓 FYP Registration Portal")

with st.form("registration_form"):
    group_name = st.text_input("Project Title")
    selected_supervisor = st.selectbox("Select Supervisor", ["-- Select --"] + supervisors)
    
    available = [s for s in all_students if s not in assigned_students]
    available.sort()
    
    m1 = st.selectbox("Member 1 (Leader)", ["-- Select --"] + available)
    m2 = st.selectbox("Member 2", ["-- Select --"] + available)
    m3 = st.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available)

    submit = st.form_submit_button("Submit Registration")

if submit:
    current_members = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or selected_supervisor == "-- Select --" or len(current_members) < 2:
        st.error("⚠️ Please fill all required fields.")
    else:
        # Prepare new row
        new_row = pd.DataFrame([{
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }])
        
        # Combine and Update Google Sheet
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(spreadsheet=url, data=updated_df)
        
        st.success("✅ Registered in Google Sheets!")
        st.balloons()
        st.rerun()

# --- DISPLAY ---
st.divider()
st.subheader("📋 Live Registrations")
st.dataframe(existing_data, use_container_width=True)