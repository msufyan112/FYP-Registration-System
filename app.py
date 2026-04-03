import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓")

# 1. PASTE YOUR GOOGLE SHEET URL HERE
# Ensure "Anyone with the link can EDIT" is turned on in Google Sheets sharing settings
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ann4DYVPMdo9kwXNfDq59WssQE49m-__l-uuYyc7Zck/edit?usp=sharing"

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Load Student List from local CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    students_path = os.path.join(current_dir, 'students.csv')
    all_students = pd.read_csv(students_path)['Name'].tolist()

    # Read existing data from Google Sheets
    try:
        # We use ttl=0 to always get the freshest data
        existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        existing_data = existing_data.dropna(how="all")
        
        assigned = []
        for col in ['Member 1', 'Member 2', 'Member 3']:
            if col in existing_data.columns:
                assigned.extend(existing_data[col].dropna().tolist())
        return all_students, assigned, existing_data
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return all_students, [], pd.DataFrame()

# Load initial data
all_students, assigned_students, existing_data = load_data()
supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]

st.title("🎓 FYP Registration Portal")

# --- THE FORM ---
with st.form("registration_form"):
    group_name = st.text_input("Project Title")
    selected_supervisor = st.selectbox("Select Supervisor", ["-- Select --"] + supervisors)
    
    available = sorted([s for s in all_students if s not in assigned_students])
    
    m1 = st.selectbox("Member 1 (Leader)", ["-- Select --"] + available)
    m2 = st.selectbox("Member 2", ["-- Select --"] + available)
    m3 = st.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available)

    submit = st.form_submit_button("Submit Registration")

if submit:
    current_members = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or selected_supervisor == "-- Select --" or len(current_members) < 2:
        st.error("⚠️ Please fill all required fields and pick at least 2 members.")
    else:
        # Create new row
        new_row = pd.DataFrame([{
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }])
        
        # Combine data
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # Save back to Google Sheets
        try:
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success("✅ Successfully registered!")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save: {e}")
            st.info("Make sure the Google Sheet is shared with 'Anyone with the link can EDIT'")

# --- DISPLAY ---
st.divider()
st.subheader("📋 Live Registrations")
st.dataframe(existing_data, use_container_width=True)
