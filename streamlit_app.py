import streamlit as st
import pandas as pd
from datetime import datetime
# from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://lihia:6Mh7dVGh0owTaYu3@study-buddy.or22n.mongodb.net/")  # Change this to your MongoDB connection string
db = client["event_db"]
collection = db["events"]

# Page title
st.title("Event Submission and Viewer")

# Event submission form
with st.form("event_form"):
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date", min_value=datetime.today())
    event_time = st.time_input("Event Time", format="hh:mm A")
    event_location = st.text_input("Event Location")
    event_description = st.text_area("Event Description")
    submit = st.form_submit_button("Submit Event")
    
    if submit and event_name and event_description and event_location:
        # Store event data in MongoDB
        event_data = {
            "Name": event_name,
            "Date": event_date.strftime('%Y-%m-%d'),
            "Time": event_time.strftime('%I:%M %p'),
            "Location": event_location,
            "Description": event_description
        }
        collection.insert_one(event_data)
        st.success("Event submitted successfully!")
        st.experimental_rerun()

# Load events from MongoDB
events = list(collection.find({}, {"_id": 0}))
if events:
    df = pd.DataFrame(events)
    st.subheader("Upcoming Events")
    
    # Display events in a table format
    selected_event = None
    for i, row in df.iterrows():
        if st.button(f"{row['Name']} ({row['Date']} @ {row['Time']}) - {row['Location']}"):
            selected_event = row
    
    # Display selected event details in a container
    if selected_event:
        with st.container():
            st.subheader(f"Details for {selected_event['Name']}")
            st.write(f"**Date:** {selected_event['Date']}")
            st.write(f"**Time:** {selected_event['Time']}")
            st.write(f"**Location:** {selected_event['Location']}")
            st.write(f"**Description:** {selected_event['Description']}")
