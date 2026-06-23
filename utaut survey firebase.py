import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ── Firebase Init ───────────────────────────────────────────────
def init_firebase():
    if not firebase_admin._apps:
        # Load credentials from Streamlit secrets or local file
        if "firebase" in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Local development - looks for service account key in same folder
            cred = credentials.Certificate("service-account-key.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

try:
    db = init_firebase()
    firebase_ok = True
except Exception as e:
    firebase_ok = False
    firebase_error = str(e)

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexera UTAUT Survey",
    page_icon="💼",
    layout="centered"
)

# ── Header ──────────────────────────────────────────────────────
st.title("💼 Nexera User Experience Survey")
st.markdown("""
This survey evaluates your experience using the **Nexera AI Job Recommendation System**.
Please answer all questions honestly based on your interaction with the system.

**Scale:** 1 = Strongly Disagree | 2 = Disagree | 3 = Neutral | 4 = Agree | 5 = Strongly Agree
""")

if not firebase_ok:
    st.warning(f"⚠️ Firebase not connected: {firebase_error}. Responses will be saved locally.")

st.divider()

# ── Participant Info ─────────────────────────────────────────────
st.subheader("📋 Participant Information")
participant_id = st.text_input("Participant ID (e.g. CV_01, CV_02...)", 
                                placeholder="Enter your participant ID")
discipline = st.selectbox("Your area of specialty", [
    "Software Development", "Data Science and Analytics", "Web Development",
    "Mobile Development", "UI/UX Design", "Graphic Design",
    "Digital Marketing", "SEO and SEM", "Social Media Management",
    "Content Writing", "Business Analysis", "Project Management",
    "Finance and Accounting", "Fintech", "Human Resources",
    "E-commerce", "Online Tutoring", "E-learning Design",
    "Customer Support", "Network Engineering", "Database Administration",
    "Cybersecurity", "Cloud Computing", "DevOps", "Other"
])
st.divider()

# ── Scale ────────────────────────────────────────────────────────
scale = {
    "1 - Strongly Disagree": 1,
    "2 - Disagree": 2,
    "3 - Neutral": 3,
    "4 - Agree": 4,
    "5 - Strongly Agree": 5
}
options = list(scale.keys())

def q(label, key):
    return st.radio(label, options, key=key, horizontal=True, index=2)

# ── Section 1: Performance Expectancy ───────────────────────────
st.subheader("Section 1: Performance Expectancy")
st.caption("Does Nexera help you achieve your job search goals?")
pe1 = q("PE1. Using Nexera helps me find relevant job opportunities more quickly.", "pe1")
pe2 = q("PE2. The job recommendations provided by Nexera match my skills and qualifications.", "pe2")
pe3 = q("PE3. Using Nexera improves my chances of finding suitable employment.", "pe3")
pe4 = q("PE4. The career path guidance provided by Nexera is useful for my professional development.", "pe4")
pe5 = q("PE5. Nexera saves me time compared to searching for jobs manually.", "pe5")
pe6 = q("PE6. The match percentage shown for each job helps me make better application decisions.", "pe6")
st.divider()

# ── Section 2: Effort Expectancy ────────────────────────────────
st.subheader("Section 2: Effort Expectancy")
st.caption("Is Nexera easy to use?")
ee1 = q("EE1. Learning to use Nexera is easy for me.", "ee1")
ee2 = q("EE2. Uploading my CV and receiving recommendations is straightforward.", "ee2")
ee3 = q("EE3. The Nexera interface is clear and easy to navigate.", "ee3")
ee4 = q("EE4. Interacting with Nexera does not require much effort.", "ee4")
ee5 = q("EE5. I was able to use Nexera without needing any external help.", "ee5")
ee6 = q("EE6. The steps required to get job recommendations on Nexera are simple and clear.", "ee6")
st.divider()

# ── Section 3: Social Influence ─────────────────────────────────
st.subheader("Section 3: Social Influence")
st.caption("Would others encourage you to use Nexera?")
si1 = q("SI1. People who are important to me would encourage me to use Nexera.", "si1")
si2 = q("SI2. I would recommend Nexera to other graduates and job seekers.", "si2")
si3 = q("SI3. I believe my peers would find Nexera useful for their job search.", "si3")
si4 = q("SI4. Using Nexera would be seen as beneficial by people around me.", "si4")
si5 = q("SI5. I have already told or would tell others about Nexera.", "si5")
si6 = q("SI6. I believe Nexera would be widely adopted among Nigerian graduates if promoted.", "si6")
st.divider()

# ── Section 4: Facilitating Conditions ──────────────────────────
st.subheader("Section 4: Facilitating Conditions")
st.caption("Do you have the resources and support to use Nexera?")
fc1 = q("FC1. I have the necessary device and internet connection to use Nexera.", "fc1")
fc2 = q("FC2. The FAQ chatbot provides adequate guidance when I need help.", "fc2")
fc3 = q("FC3. I have the knowledge and skills required to use Nexera.", "fc3")
fc4 = q("FC4. I feel confident using Nexera without external assistance.", "fc4")
fc5 = q("FC5. The instructions and labels within Nexera are sufficient to guide me.", "fc5")
fc6 = q("FC6. I would have no difficulty accessing and using Nexera on my preferred device.", "fc6")
st.divider()

# ── Comments ─────────────────────────────────────────────────────
st.subheader("Additional Comments (Optional)")
comments = st.text_area("Any other feedback about your experience with Nexera?",
                         placeholder="Type your comments here...")

# ── Submit ───────────────────────────────────────────────────────
st.divider()
submitted = st.button("✅ Submit Response", type="primary", use_container_width=True)

if submitted:
    if not participant_id.strip():
        st.error("Please enter your Participant ID before submitting.")
    else:
        # Build response
        pe_mean = round((scale[pe1]+scale[pe2]+scale[pe3]+scale[pe4]+scale[pe5]+scale[pe6])/6, 2)
        ee_mean = round((scale[ee1]+scale[ee2]+scale[ee3]+scale[ee4]+scale[ee5]+scale[ee6])/6, 2)
        si_mean = round((scale[si1]+scale[si2]+scale[si3]+scale[si4]+scale[si5]+scale[si6])/6, 2)
        fc_mean = round((scale[fc1]+scale[fc2]+scale[fc3]+scale[fc4]+scale[fc5]+scale[fc6])/6, 2)
        overall = round((pe_mean+ee_mean+si_mean+fc_mean)/4, 2)

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "participant_id": participant_id.strip(),
            "discipline": discipline,
            "PE1": scale[pe1], "PE2": scale[pe2], "PE3": scale[pe3],
            "PE4": scale[pe4], "PE5": scale[pe5], "PE6": scale[pe6],
            "EE1": scale[ee1], "EE2": scale[ee2], "EE3": scale[ee3],
            "EE4": scale[ee4], "EE5": scale[ee5], "EE6": scale[ee6],
            "SI1": scale[si1], "SI2": scale[si2], "SI3": scale[si3],
            "SI4": scale[si4], "SI5": scale[si5], "SI6": scale[si6],
            "FC1": scale[fc1], "FC2": scale[fc2], "FC3": scale[fc3],
            "FC4": scale[fc4], "FC5": scale[fc5], "FC6": scale[fc6],
            "comments": comments,
            "PE_mean": pe_mean,
            "EE_mean": ee_mean,
            "SI_mean": si_mean,
            "FC_mean": fc_mean,
            "overall_mean": overall
        }

        # Save to Firebase
        if firebase_ok:
            try:
                db.collection("utaut_responses").document(
                    participant_id.strip()
                ).set(row)
                st.success(f"✅ Response saved to Firebase! Thank you, {participant_id}.")
            except Exception as e:
                st.error(f"Firebase save failed: {e}")
                # Fallback to CSV
                df_new = pd.DataFrame([row])
                if os.path.exists("utaut_responses.csv"):
                    df_ex = pd.read_csv("utaut_responses.csv")
                    df_all = pd.concat([df_ex, df_new], ignore_index=True)
                else:
                    df_all = df_new
                df_all.to_csv("utaut_responses.csv", index=False)
                st.info("Saved locally as backup.")
        else:
            # Save locally
            df_new = pd.DataFrame([row])
            if os.path.exists("utaut_responses.csv"):
                df_ex = pd.read_csv("utaut_responses.csv")
                df_all = pd.concat([df_ex, df_new], ignore_index=True)
            else:
                df_all = df_new
            df_all.to_csv("utaut_responses.csv", index=False)
            st.success(f"✅ Response saved locally! Thank you, {participant_id}.")

        st.info(f"**Your scores:** PE: {pe_mean} | EE: {ee_mean} | SI: {si_mean} | FC: {fc_mean} | Overall: {overall}")

# ── Live Dashboard ───────────────────────────────────────────────
st.divider()
st.subheader("📊 Live Results Dashboard")

# Try to load from Firebase first
responses = []
if firebase_ok:
    try:
        docs = db.collection("utaut_responses").stream()
        for doc in docs:
            responses.append(doc.to_dict())
    except:
        pass

# Fallback to CSV
if not responses and os.path.exists("utaut_responses.csv"):
    df = pd.read_csv("utaut_responses.csv")
    responses = df.to_dict("records")

if responses:
    df = pd.DataFrame(responses)
    st.write(f"**Total responses: {len(df)} / 50**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Performance Expectancy", f"{df['PE_mean'].mean():.2f}/5.00")
    col2.metric("Effort Expectancy", f"{df['EE_mean'].mean():.2f}/5.00")
    col3.metric("Social Influence", f"{df['SI_mean'].mean():.2f}/5.00")
    col4.metric("Facilitating Conditions", f"{df['FC_mean'].mean():.2f}/5.00")
    st.success(f"**Overall Mean: {df['overall_mean'].mean():.2f} / 5.00**")

    # Download CSV button
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download All Responses as CSV",
        data=csv_data,
        file_name="utaut_responses.csv",
        mime="text/csv"
    )
else:
    st.info("No responses yet. Be the first to submit!")
