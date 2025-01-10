import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
def connect_to_mongo():
    client = MongoClient("mongodb+srv://mouliinindia05:mouli05052002@cluster0.o6dco.mongodb.net/")
    db = client['WaterborneDiseases']  # Use the existing 'WaterborneDiseases' database
    return db

# Read the CSV file
csv_file_path = 'D:/ML-PROJECTS/Water Borne Diseases/updated_disease_dataset_bangalore.csv'  # Replace with the path to your CSV file
data_frame = pd.read_csv(csv_file_path)

# Convert DataFrame rows to dictionary format for MongoDB insertion
data_dict = data_frame.to_dict(orient='records')

# Connect to MongoDB and get the 'patient_details' collection in the 'WaterborneDiseases' database
db = connect_to_mongo()
patients_collection = db['patient_details']  # This creates a new collection named 'patient_details'

# Insert the data into the MongoDB collection
patients_collection.insert_many(data_dict)

print("CSV data has been successfully inserted into the 'patient_details' collection in the 'WaterborneDiseases' database.")
