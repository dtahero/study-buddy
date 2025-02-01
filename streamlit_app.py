import streamlit as st
import pandas as pd
from datetime import datetime

# Page title
st.title("Event Submission and Viewer")

# Initialize session state for storing events if not already present
if "events" not in st.session_state:
    st.session_state.events = []

# Event submission form
with st.form("event_form"):
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date", min_value=datetime.today())
    event_time = st.time_input("Event Time")
    event_description = st.text_area("Event Description")
    submit = st.form_submit_button("Submit Event")
    
    if submit and event_name and event_description:
        # Store event data
        st.session_state.events.append({
            "Name": event_name,
            "Date": event_date.strftime('%Y-%m-%d'),
            "Time": event_time.strftime('%H:%M'),
            "Description": event_description
        })
        st.success("Event submitted successfully!")

# Convert event data to DataFrame
if st.session_state.events:
    df = pd.DataFrame(st.session_state.events)
    st.subheader("Upcoming Events")
    
    # Store selected event in session state
    if "selected_event" not in st.session_state:
        st.session_state.selected_event = None
    
    for i, row in df.iterrows():
        if st.button(f"{row['Name']} ({row['Date']} @ {row['Time']})"):
            st.session_state.selected_event = row.to_dict()  # Store as dictionary
    
    # Display selected event details in a container
    if st.session_state.selected_event:
        with st.container():
            st.subheader(f"Details for {st.session_state.selected_event['Name']}")
            st.write(f"**Date:** {st.session_state.selected_event['Date']}")
            st.write(f"**Time:** {st.session_state.selected_event['Time']}")
            st.write(f"**Description:** {st.session_state.selected_event['Description']}")
