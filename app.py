import streamlit as st
import pandas as pd
import requests
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓")

# 1. PASTE YOUR SHEET ID HERE
# Your Sheet ID is the long string in your URL between /d/ and /edit
# Example: https://docs.google.com/spreadsheets/d/1ABC123_XYZ/edit -> ID is 1ABC123_XYZ
SHEET_ID = "1ann4DYVPMdo9kwXNfDq59WssQE49m-__l-uuYyc7Zck"
SHEET_NAME = "Sheet1"  # Make sure this matches your tab name at the bottom

# Construct the Export URL
CSV_URL = f"https://docs.google.com/spreadsheets/d/{1ann4DYVPMdo9kwXNfDq59WssQE49m-__l-uuYyc7Zck}/gviz/tq?tqx=out:csv&sheet={Sheet1}"

def load_data():
    # Load Student List from local CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    students_path = os.path.join(current_dir, 'students.csv')
    all_students = pd.read_csv(students_path)['Name'].tolist()

    # Read existing data using pandas direct CSV link
    try:
        existing_data = pd.read_csv(CSV_URL)
        existing_data = existing_data.dropna(how="all")
        
        assigned = []
        for col in ['Member 1', 'Member 2', 'Member 3']:
            if col in existing_data.columns:
                assigned.extend(existing_data[col].dropna().tolist())
        return all_students, assigned, existing_data
    except Exception as e:
        return all_students, [], pd.DataFrame(columns=['Group Name', 'Supervisor', 'Member 1', 'Member 2', 'Member 3'])

all_students, assigned_students, existing_data = load_data()
supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]

st.title("🎓 FYP Registration Portal")

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
        st.error("⚠️ Please fill all fields.")
    else:
        # We use a Google Form "Pre-filled Link" style or a simple Apps Script for Writing
        # Since Writing to Sheets is restricted, the EASIEST way for a student project
        # is to use a Google Form to collect data, then read the Sheet here.
        
        st.warning("To save data securely, please use the Google Form link provided by your admin.")
        st.info("Reading data from Google Sheets is working! Saving requires a 'Service Account' for security.")

# --- DISPLAY ---
st.divider()
st.subheader("📋 Registered Groups (Live from Sheets)")
st.dataframe(existing_data, use_container_width=True)
