import requests
import pandas as pd
import random
import time

# Load the crop data
file_path = "C:/Users/user/Documents/Sujay/Study/Project/AI based crop recommendation/ML_Model/Crop_recommendation.csv"  # Update this with your actual path
crop_data = pd.read_csv(file_path)

while True:

    # Select a random row from the dataset
    random_row = crop_data.sample(n=1).iloc[0]

    # Convert values to standard Python types for JSON serialization
    soil_data = {
        "N": int(random_row["N"]),
        "P": int(random_row["P"]),
        "K": int(random_row["K"]),
        "temperature": float(random_row["temperature"]),
        "humidity": float(random_row["humidity"]),
        "ph": float(random_row["ph"]),
        "rainfall": float(random_row["rainfall"])  # Ensure rainfall is also a float
    }

    # Send the data to the Flask server
    response = requests.post("http://192.168.0.107:5003/send_soil_data", json=soil_data)
    print(response.json())
    time.sleep(1)
