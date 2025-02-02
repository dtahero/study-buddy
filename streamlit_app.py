import streamlit as st
import pandas as pd
from datetime import datetime, time
from pymongo import MongoClient

# Connect to MongoDB
try:
    client = MongoClient("mongodb+srv://lihia:6Mh7dVGh0owTaYu3@study-buddy.or22n.mongodb.net/?retryWrites=true&w=majority")
    db = client["event_db"]
    collection = db["events"]
except Exception as e:
    st.error(f"Failed to connect to MongoDB: {e}")

# Custom CSS to center the image
st.markdown(
    """
    <style>
    .center {
        justify-content: center;
        display: flex;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="center"><img src="https://github.com/dtahero/study-buddy/blob/main/IMG_7441.PNG?raw=true" width="500"></div>', unsafe_allow_html=True)

# Function to convert military time to standard time (12-hour format with AM/PM)
def convert_to_standard_time(military_time):
    try:
        time_obj = datetime.strptime(military_time, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except ValueError:
        return military_time

# Function to generate standard time options for the dropdown
def generate_standard_time_options():
    times = []
    for hour in range(0, 24):
        for minute in range(0, 60, 15):  # 15-minute intervals
            time_obj = time(hour, minute)
            times.append(time_obj.strftime("%I:%M %p"))
    return times

# Page title
st.subheader("Open Study Sessions:")

# Load events from MongoDB
events = list(collection.find({}, {"_id": 0}))
if events:
    # Convert events to a DataFrame
    df = pd.DataFrame(events)
    
    # Convert 'Date' and 'Time' to datetime for sorting
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    
    # Sorting dropdown
    sort_by = st.selectbox("Sort events by", ["Date", "Name"])
    
    # Sort events based on the selected option
    if sort_by == "Date":
        df = df.sort_values(by='DateTime', ascending=False)
    elif sort_by == "Name":
        df = df.sort_values(by='Name', ascending=True)

    # Display events
    for i, row in df.iterrows():
        display_time = convert_to_standard_time(row['Time'])
        
        # Display event information
        if st.button(f"{row['Name']} @ {row['Location']} | {row['Date']} @ {display_time}",
                     key=f"button_{i}",
                     use_container_width=True):
            st.write(f"**Event Name**: {row['Name']}")
            st.write(f"**Date**: {row['Date']}")
            st.write(f"**Time**: {display_time}")
            st.write(f"**Location**: {row['Location']}")
            st.write(f"**Description**: {row['Description']}")

# Event submission form
st.subheader("Event Submission Form")

with st.form("event_form"):
    event_name = st.text_input("Session Name and Subject")
    event_date = st.date_input("Session Date", min_value=datetime.today())
    time_options = generate_standard_time_options()
    event_time_str = st.selectbox("Session Time", options=time_options)
    event_location = st.text_input("Location")
    event_description = st.text_area("Description")
    submit = st.form_submit_button("Submit")
    
    if submit:
        if event_name and event_description and event_location:
            event_time_obj = datetime.strptime(event_time_str, "%I:%M %p").time()
            event_time_military = event_time_obj.strftime("%H:%M")
            
            event_data = {
                "Name": event_name,
                "Date": event_date.strftime('%Y-%m-%d'),
                "Time": event_time_military,
                "Location": event_location,
                "Description": event_description
            }
            collection.insert_one(event_data)
            st.success("Event submitted successfully!")
            st.experimental_rerun()
        else:
            st.error("Please fill in all required fields")
