import streamlit as st
from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb+srv://itz4mealone:SportsMentor@cluster0.gcagz.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "test"
USERS_COLLECTION = "users"
REQUESTS_COLLECTION = "requests"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[USERS_COLLECTION]
requests_collection = db[REQUESTS_COLLECTION]

# Synonym Mapping for Expertise Matching
synonym_mapping = {
    "batter": ["batting", "batting coach"],
    "bowler": ["bowling", "bowling coach"],
    "all-rounder": ["batting", "bowling", "fielding"],
    "fast bowler": ["fast bowling", "pace bowling", "bowling coach"],
    "spin bowler": ["spin bowling", "leg spin", "off spin", "spin coach"],
    "wicketkeeper": ["wicketkeeping", "keeper"],
    "fielder": ["fielding", "fielding coach"],
}

# Function to Find Mentor
def find_mentor(athlete_name):
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
    return mentors if mentors else "❌ No suitable mentor found"

# Function to Send Request
def send_request(athlete_name, mentor_name):
    existing_request = requests_collection.find_one({
        "athlete_name": athlete_name,
        "mentor_name": mentor_name
    })

    if existing_request:
        return "⚠ Request already sent to this mentor."

    requests_collection.insert_one({
        "athlete_name": athlete_name,
        "mentor_name": mentor_name,
        "status": "pending"
    })
    return "✅ Request sent successfully!"

# Streamlit UI
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🏆 SportsMentor: Find Your Mentor!</h1>", unsafe_allow_html=True)

athlete_name = st.text_input("Enter Athlete Name")

if st.button("Find Mentor"):
    mentors = find_mentor(athlete_name)

    if isinstance(mentors, list) and mentors:
        st.success(f"✅ Found {len(mentors)} mentor(s)")

        for mentor in mentors:
            st.markdown(
                f"""
                <div style='background-color: #fff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); margin-top: 15px;'>
                    <h4>👤 {mentor.get('name', 'N/A')}</h4>
                    <p><b>Sport:</b> {mentor.get('mentorSport', 'N/A')}</p>
                    <p><b>Region:</b> {mentor.get('mentorRegion', 'N/A')}</p>
                    <p><b>Expertise:</b> {mentor.get('mentorExpertise', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Request Button for Each Mentor
            if st.button(f"Request {mentor.get('name')}", key=f"request_{mentor.get('name')}"):
                result = send_request(athlete_name, mentor.get('name'))
                st.write(result)
    else:
        st.warning("No mentors found.")
