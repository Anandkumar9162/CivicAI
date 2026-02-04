# This File Run streamlit run app.py command.
import streamlit as st
import google.generativeai as genai
from PIL import Image
from geopy.geocoders import Nominatim
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CivicAI", page_icon="🚧", layout="wide")

st.title("🚧 CivicAI: Smart Reporting System")

# Sidebar for Admin & API Key
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    admin_mode = st.checkbox("🔓 Admin Mode (View Reports)")

# --- 2. FUNCTIONS ---
def analyze_image(image, key):
    if not key: return "⚠️ API Key Missing"
    genai.configure(api_key=key)
    
    # Model: Gemini 2.0 Flash Exp (Jo tere paas chal raha hai)
    # Ye sabse stable wala hai
    model = genai.GenerativeModel("gemini-flash-latest")
    
    # Prompt updated (Street Light bhi add kiya hai)
    prompt = """
    Analyze this image for civic issues like:
    1. Potholes
    2. Garbage Dumps
    3. Broken Street Lights
    4. Water Logging/Drainage
    
    Identify the issue & severity.
    If the image is a person, selfie, or unrelated object, reply exactly: "INVALID IMAGE"
    """
    
    try:
        return model.generate_content([prompt, image]).text
    except Exception as e:
        return f"Error: {str(e)}"

def save_report(issue, location, lat, lon):
    # Data CSV file mein save karna
    file_name = "reports.csv"
    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "Issue": [issue],
        "Location": [location],
        "Latitude": [lat],
        "Longitude": [lon],
        "Status": ["Pending"]
    }
    df = pd.DataFrame(data)
    
    if not os.path.isfile(file_name):
        df.to_csv(file_name, index=False)
    else:
        df.to_csv(file_name, mode='a', header=False, index=False)

# --- 3. MAIN APP LOGIC ---

if admin_mode:
    # --- ADMIN DASHBOARD (Nagar Nigam View) ---
    st.header("📋 Admin Dashboard")
    
    # Clear Data Button
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🗑️ Clear All Data"):
            if os.path.exists("reports.csv"):
                os.remove("reports.csv")
                st.success("Data Deleted!")
                st.rerun()

    if os.path.exists("reports.csv"):
        df = pd.read_csv("reports.csv")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("📍 Issue Hotspots")
        # Map tabhi dikhega jab Latitude column hoga
        if not df.empty and 'Latitude' in df.columns:
            st.map(df[['Latitude', 'Longitude']].rename(columns={'Latitude':'lat', 'Longitude':'lon'}))
    else:
        st.info("No reports submitted yet.")

else:
    # --- USER REPORTING FORM ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Upload Evidence 📸")
        tab1, tab2 = st.tabs(["Camera", "Gallery"])
        image_data = None
        with tab1:
            cam = st.camera_input("Click Photo")
            if cam: image_data = cam
        with tab2:
            upl = st.file_uploader("Upload", type=['jpg','png'])
            if upl: image_data = upl

    with col2:
        st.subheader("2. Location Details 📍")
        loc_input = st.text_input("Area Name (e.g. Boring Road, Patna)")
        lat, lon = None, None
        
        if loc_input:
            geolocator = Nominatim(user_agent="civic_ai_app_v2")
            location = geolocator.geocode(loc_input)
            if location:
                lat, lon = location.latitude, location.longitude
                st.success(f"✅ Found: {location.address}")
                st.map(data={'lat': [lat], 'lon': [lon]}) # Live map preview
            else:
                st.error("❌ Location not found! Try adding City name.")

    # --- SUBMIT BUTTON WITH LOGIC ---
    st.markdown("---")
    if st.button("🚀 Submit Complaint"):
        if image_data and api_key and lat:
            # 1. Image Open
            img = Image.open(image_data)
            
            with st.spinner("🤖 AI Analyzing..."):
                # 2. AI Check
                report_text = analyze_image(img, api_key)
                
                # --- GATEKEEPER LOGIC (CHECK INVALID) ---
                if "INVALID" in report_text:
                    st.error("❌ Complaint Rejected: This image does not show a civic issue.")
                    st.warning(f"AI Reason: {report_text}")
                    # Note: Humne save_report call NAHI kiya yahan
                else:
                    # Valid hai -> Save karo
                    save_report(report_text, loc_input, lat, lon)
                    st.success("✅ Complaint Registered Successfully!")
                    st.info(f"AI Report: {report_text}")
                    
        else:
            st.error("Please provide Photo, Location & API Key!")