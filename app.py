import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Custom CSS for styling
st.markdown(
    """
    <style>
        body {
            background-color: #f4f4f4;
        }
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 20px;
        }
        .box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
        .mentor-card {
            background-color: #fff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin-top: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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
st.markdown("<div class='title'>🏆 SportsMentor: Find Your Mentor!</div>", unsafe_allow_html=True)

st.markdown("<div class='box'>", unsafe_allow_html=True)
athlete_name = st.text_input("Enter Athlete Name")
st.markdown("</div>", unsafe_allow_html=True)

if st.button("Find Mentor", help="Click to search for mentors"):
    mentors = find_mentor(athlete_name)

    if isinstance(mentors, list) and mentors:
        st.success(f"✅ Found {len(mentors)} mentor(s)")

        # Display mentors in styled cards
        for mentor in mentors:
            st.markdown(
                f"""
                <div class='mentor-card'>
                    <h4>👤 {mentor.get('name', 'N/A')}</h4>
                    <p><b>Sport:</b> {mentor.get('mentorSport', 'N/A')}</p>
                    <p><b>Region:</b> {mentor.get('mentorRegion', 'N/A')}</p>
                    <p><b>Expertise:</b> {mentor.get('mentorExpertise', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("No mentors found.")
