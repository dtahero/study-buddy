import streamlit as st
import pandas as pd
from datetime import datetime, time
from pymongo import MongoClient

# Connect to MongoDB
try:
    client = MongoClient("mongodb+srv://lihia:6Mh7dVGh0owTaYu3@study-buddy.or22n.mongodb.net/?retryWrites=true&w=majority")
    db = client["event_db"]
    collection = db["events"]
    st.success("Connected to MongoDB successfully!")
except Exception as e:
    st.error(f"Failed to connect to MongoDB: {e}")

# Function to convert military time to standard time (12-hour format with AM/PM)
def convert_to_standard_time(military_time):
    try:
        # Parse the military time string into a datetime object
        time_obj = datetime.strptime(military_time, "%H:%M")
        # Convert to 12-hour format with AM/PM
        return time_obj.strftime("%I:%M %p")
    except ValueError:
        return military_time  # Return the original time if conversion fails

# Function to generate standard time options for the dropdown
def generate_standard_time_options():
    times = []
    for hour in range(0, 24):
        for minute in range(0, 60, 15):  # 15-minute intervals
            time_obj = time(hour, minute)
            times.append(time_obj.strftime("%I:%M %p"))  # Convert to 12-hour format
    return times

# Page title
st.title("Study Buddy")

# Event submission form
with st.form("event_form"):
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date", min_value=datetime.today())
    
    # Custom dropdown for standard time selection
    time_options = generate_standard_time_options()
    event_time_str = st.selectbox("Event Time", options=time_options)
    
    event_location = st.text_input("Event Location")
    event_description = st.text_area("Event Description")
    submit = st.form_submit_button("Submit Event")
    
    if submit:
        st.write("Submit button clicked")
        if event_name and event_description and event_location:
            st.write("All required fields are filled")
            # Convert selected standard time back to military time for storage
            event_time_obj = datetime.strptime(event_time_str, "%I:%M %p").time()
            event_time_military = event_time_obj.strftime("%H:%M")
            
            # Store event data in MongoDB (in military time for consistency)
            event_data = {
                "Name": event_name,
                "Date": event_date.strftime('%Y-%m-%d'),
                "Time": event_time_military,  # Store in military time
                "Location": event_location,
                "Description": event_description
            }
            collection.insert_one(event_data)
            st.success("Event submitted successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields")

# Load events from MongoDB
events = list(collection.find({}, {"_id": 0}))
if events:
    df = pd.DataFrame(events)
    st.subheader("Upcoming Events")
    
    # Display events in a table format
    selected_event = None
    for i, row in df.iterrows():
        # Convert military time to standard time for display
        display_time = convert_to_standard_time(row['Time'])
        if st.button(f"{row['Name']} ({row['Date']} @ {display_time}) - {row['Location']}"):
            selected_event = row
    
    # Display selected event details in a container
    if selected_event is not None:
        with st.container():
            st.subheader(f"Details for {selected_event['Name']}")
            st.write(f"**Date:** {selected_event['Date']}")
            # Convert and display time in standard time
            display_time = convert_to_standard_time(selected_event['Time'])
            st.write(f"**Time:** {display_time}")
            st.write(f"**Location:** {selected_event['Location']}")
            st.write(f"**Description:** {selected_event['Description']}")