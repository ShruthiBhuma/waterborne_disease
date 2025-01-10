import streamlit as st
import numpy as np
import tensorflow as tf
import random
from geopy.geocoders import Nominatim
from pymongo import MongoClient
from datetime import datetime
import bcrypt

# Load the saved model
model = tf.keras.models.load_model('D:/ML-PROJECTS/Water Borne Diseases/model/waterborne_disease_model.h5')

dict_rev = {
    0: 'Rift_Valley_fever', 1: 'Chikungunya', 2: 'Yellow_Fever',
    3: 'Japanese_encephalitis', 4: 'Zika', 5: 'Dengue',
    6: 'West_Nile_fever', 7: 'Malaria'
}

features = [
    "sudden_fever", "headache", "mouth_bleed", "nose_bleed", "muscle_pain",
    "joint_pain", "vomiting", "rash", "diarrhea", "hypotension",
    "pleural_effusion", "ascites", "gastro_bleeding", "swelling", "nausea",
    "chills", "myalgia", "digestion_trouble", "fatigue", "skin_lesions",
    "stomach_pain", "orbital_pain", "neck_pain", "weakness", "back_pain",
    "weight_loss", "gum_bleed", "jaundice", "coma", "dizziness",
    "inflammation", "red_eyes", "loss_of_appetite", "urination_loss",
    "slow_heart_rate", "abdominal_pain", "light_sensitivity", "yellow_skin",
    "yellow_eyes", "facial_distortion", "microcephaly", "rigor",
    "bitter_tongue", "convulsion", "anemia", "cocacola_urine", "hypoglycemia",
    "prostraction", "hyperpyrexia", "stiff_neck", "irritability", "confusion",
    "tremor", "paralysis", "lymph_swells", "breathing_restriction",
    "toe_inflammation", "finger_inflammation", "lips_irritation", "itchiness",
    "ulcers", "toenail_loss", "speech_problem", "bullseye_rash"
]

# Connect to MongoDB
def connect_to_mongo():
    client = MongoClient("mongodb+srv://mouliinindia05:mouli05052002@cluster0.o6dco.mongodb.net/")
    db = client['WaterborneDiseases']
    return db

# Predict disease
def predict_disease(inputs):
    inputs = np.array(inputs, dtype=np.float32).reshape(1, -1)
    predictions = model.predict(inputs)
    top_1_id = np.argmax(predictions, axis=1)[0]
    return dict_rev[top_1_id]

# Get latitude and longitude from city
def get_latitude_longitude(city_name):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    return None, None

st.sidebar.title("Navigation")
pages = st.sidebar.radio("Go to", ["Signup", "Login", "Predict"])

db = connect_to_mongo()

if pages == "Signup":
    st.title("Signup Page")
    patient_name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    city = st.text_input("Enter your city")  # Asking for city during signup
    
    if st.button("Signup"):
        users_collection = db['users']
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            st.error("Email already exists. Please login.")
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            latitude, longitude = get_latitude_longitude(city)  # Get latitude and longitude from city name
            if latitude and longitude:
                user_data = {
                    "patient_name": patient_name,
                    "email": email,
                    "password": hashed_password.decode('utf-8'),
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city
                }
                users_collection.insert_one(user_data)
                st.success("Signup successful! Please login.")
            else:
                st.error("Unable to find the location for the provided city. Please try again.")

elif pages == "Login":
    st.title("Login Page")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    
    if st.button("Login"):
        users_collection = db['users']
        user = users_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            st.success(f"Welcome back, {user['patient_name']}!")
            st.session_state['logged_in'] = True
            st.session_state['user_data'] = user
        else:
            st.error("Invalid email or password.")

elif pages == "Predict" and st.session_state.get('logged_in', False):
    st.title("Prediction Page")
    user_data = st.session_state['user_data']
    
    user_inputs = {}
    input_features = [
        "sudden_fever", "headache", "vomiting", "diarrhea", "hypotension",
        "jaundice", "fatigue", "stomach_pain", "rash", "weight_loss",
        "abdominal_pain", "yellow_eyes", "nausea", "back_pain", "chills"
    ]
    
    for feature in input_features:
        value = st.selectbox(f"Do you have {feature.replace('_', ' ')}?", ["No", "Yes"], key=feature)
        user_inputs[feature] = "Yes" if value == "Yes" else "No"
    
    all_inputs = [1 if user_inputs.get(feature, "No") == "Yes" else 0 for feature in features]
    
    if st.button("Predict"):
        yes_count = sum([1 for v in user_inputs.values() if v == "Yes"])
        
        if yes_count <= 2:
            st.success("You are healthy!")
        else:
            top_disease = predict_disease(all_inputs)
            st.success(f"You might have {top_disease}. Please meet a medical professional.")
            
            # Save to MongoDB
            patients_collection = db['patients']
            prediction_data = {
                "patient_name": user_data['patient_name'],
                "latitude": user_data['latitude'],
                "longitude": user_data['longitude'],
                "city": user_data['city'],
                "features": user_inputs,
                "predicted_disease": top_disease,
                "date_of_diagnosis": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            patients_collection.insert_one(prediction_data)
            st.success("Your data has been saved to the database.")
