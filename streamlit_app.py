import streamlit as st
import pandas as pd
from datetime import datetime, time
from pymongo import MongoClient

# Set Streamlit page config
st.set_page_config(page_title="Study Buddy", layout="wide")

# Connect to MongoDB
try:
    client = MongoClient("mongodb+srv://lihia:6Mh7dVGh0owTaYu3@study-buddy.or22n.mongodb.net/?retryWrites=true&w=majority")
    db = client["event_db"]
    collection = db["events"]
except Exception as e:
    st.error(f"Failed to connect to MongoDB: {e}")

# Custom CSS for rounded containers, box shadows, and colors
st.markdown(
    """
    <style>
        body {
            background-color: #f8f9fa;
        }
        .container {
            background: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
        }
        .event-container {
            background: linear-gradient(135deg, #ffffff, #f1f1f1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 12px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
        }
        .expander-box {
            background: #fff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Centered logo
st.markdown('<div style="display: flex; justify-content: center;"><img src="https://github.com/dtahero/study-buddy/blob/main/IMG_7441.PNG?raw=true" width="400"></div>', unsafe_allow_html=True)

# Event submission form with rounded container
st.subheader("📅 Add a New Study Session")

with st.form("event_form"):
    with st.expander("➕ Click to Add Event", expanded=True):
# st.markdown('<div class="expander-box">', unsafe_allow_html=True)

        event_name = st.text_input("📖 Session Name and Subject")
        event_date = st.date_input("📅 Session Date", min_value=datetime.today())
        time_options = generate_standard_time_options()
        event_time_str = st.selectbox("⏰ Session Time", options=time_options)
        event_location = st.text_input("📍 Location")
        event_description = st.text_area("📝 Description")

        submit = st.form_submit_button("🚀 Submit")

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
                st.success("🎉 Event submitted successfully!")
                st.rerun()
            else:
                st.error("⚠️ Please fill in all required fields.")

        st.markdown('</div>', unsafe_allow_html=True)

# Page title
st.subheader("📌 Open Study Sessions")

# Load events from MongoDB
events = list(collection.find({}, {"_id": 0}))

# Sorting dropdown
sort_by = st.selectbox("🔍 Sort events by", ["Date", "Name"])

if events:
    with st.container():
        # st.markdown('<div class="container">', unsafe_allow_html=True)

        # Convert events to a DataFrame
        df = pd.DataFrame(events)

        # Convert 'Date' and 'Time' to datetime for sorting
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

        # Sort events based on the selected option
        if sort_by == "Date":
            df = df.sort_values(by='DateTime', ascending=False)
        elif sort_by == "Name":
            df = df.sort_values(by='Name', ascending=True)

        # Display events
        @st.dialog("Event Details", width="large")
        def show_event_details(row):
            display_time = convert_to_standard_time(row['Time'])
            st.write(f"**📖 Event Name**: {row['Name']}")
            st.write(f"**📝 Description**: {row['Description']}")
            st.write(f"**📅 Date**: {row['Date']}")
            st.write(f"**⏰ Time**: {display_time}")
            st.write(f"**📍 Location**: {row['Location']}")

        if "dialog_open" not in st.session_state:
            st.session_state.dialog_open = False

        # Scrollable section for events
        with st.container(border=True, height=500):
            for i, row in df.iterrows():
                display_time = convert_to_standard_time(row['Time'])

                # **Keeping event buttons the same**
                if st.button(f"{row['Name']} @ {row['Location']} | {row['Date']} @ {display_time}",
                             key=f"button_{i}",
                             use_container_width=True):
                    st.session_state.dialog_open = True
                    show_event_details(row)

        st.markdown('</div>', unsafe_allow_html=True)
