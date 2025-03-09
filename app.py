import streamlit as st
from pymongo import MongoClient
import pandas as pd

# MongoDB Connection
MONGO_URI = "mongodb+srv://itz4mealone:SportsMentor@cluster0.gcagz.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "test"
COLLECTION_NAME = "users"
REQUESTS_COLLECTION = "requests"

# Synonym Mapping for Expertise Matching
synonym_mapping = {
    "batter": ["batting", "batting coach"],
    "bowler": ["bowling", "bowling coach"],
    "all-rounder": ["batting", "bowling", "fielding"],
    "fast bowler": ["fast bowling", "pace bowling", "fast bowler", "bowling coach"],
    "pace bowler": ["fast bowling", "pace bowling", "fast bowler", "bowling coach"],
    "spin bowler": ["spin bowling", "leg spin", "off spin", "spin coach"],
    "wicketkeeper": ["wicketkeeping", "wicketkeeper", "keeper"],
    "fielder": ["fielding", "fielding coach"],
}

# Function to Find Mentor
def find_mentor(athlete_name):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db[COLLECTION_NAME]

    # Find the athlete
    athlete = users_collection.find_one({"name": athlete_name, "role": "athlete"})
    if not athlete:
        return "❌ Athlete not found"

    athlete_sport = athlete.get("athleteSport")
    athlete_region = athlete.get("athleteRegion")
    athlete_position = athlete.get("athleteposition", "").lower()
    
    expertise_keywords = synonym_mapping.get(athlete_position, [athlete_position])

    mentor_query = {
        "role": "mentor",
        "mentorSport": athlete_sport,
        "mentorRegion": athlete_region,
        "$or": [{"mentorExpertise": {"$regex": f".*{kw}.*", "$options": "i"}} for kw in expertise_keywords]
    }
    
    mentors = list(users_collection.find(mentor_query, {"_id": 0}))
    client.close()
    return mentors if mentors else "❌ No suitable mentor found"

# Function to Send Mentor Request
def send_request(athlete_name, mentor_name):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    requests_collection = db[REQUESTS_COLLECTION]
    
    request_data = {"athlete": athlete_name, "mentor": mentor_name, "status": "pending"}
    requests_collection.insert_one(request_data)
    client.close()
    
    st.success(f"📩 Request sent to {mentor_name}!")

# Streamlit UI
st.title("🏆 SportsMentor: Find Your Mentor!")
athlete_name = st.text_input("Enter Athlete Name")

if st.button("Find Mentor"):
    mentors = find_mentor(athlete_name)
    if isinstance(mentors, list) and mentors:
        st.success(f"✅ Found {len(mentors)} mentor(s)")
        for mentor in mentors:
            mentor_name = mentor.get("name", "N/A")
            with st.container():
                st.write(f"**👤 {mentor_name}**")
                st.write(f"**Sport:** {mentor.get('mentorSport', 'N/A')}")
                st.write(f"**Region:** {mentor.get('mentorRegion', 'N/A')}")
                st.write(f"**Expertise:** {mentor.get('mentorExpertise', 'N/A')}")
                if st.button(f"Request {mentor_name}", key=mentor_name):
                    send_request(athlete_name, mentor_name)
    else:
        st.warning("No mentors found.")
