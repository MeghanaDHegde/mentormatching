import streamlit as st
from pymongo import MongoClient
import pandas as pd

# MongoDB Connection
MONGO_URI = "mongodb+srv://itz4mealone:SportsMentor@cluster0.gcagz.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "test"
COLLECTION_NAME = "users"

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

    # Extract athlete details
    athlete_sport = athlete.get("athleteSport")
    athlete_region = athlete.get("athleteRegion")
    athlete_position = athlete.get("athleteposition", "").lower()

    # Map synonyms
    expertise_keywords = synonym_mapping.get(athlete_position, [athlete_position])

    # Query to find mentors
    mentor_query = {
        "role": "mentor",
        "mentorSport": athlete_sport,
        "mentorRegion": athlete_region,
        "$or": [{"mentorExpertise": {"$regex": f".*{kw}.*", "$options": "i"}} for kw in expertise_keywords]
    }

    # Fetch mentors
    mentors = list(users_collection.find(mentor_query, {"_id": 0}))  # Exclude ObjectId

    client.close()
    return mentors if mentors else "❌ No suitable mentor found"

# Streamlit UI
st.title("🏆 SportsMentor: Find Your Mentor!")

# User input
athlete_name = st.text_input("Enter Athlete Name")

if st.button("Find Mentor"):
    mentors = find_mentor(athlete_name)

    if isinstance(mentors, list):
        if mentors:
            st.success(f"✅ Found {len(mentors)} mentor(s)")
            st.json(mentors)  # Display JSON output
            df = pd.DataFrame(mentors)
            st.dataframe(df)  # Display as table
        else:
            st.warning("No mentors found.")
    else:
        st.error(mentors)  # Display error messages
