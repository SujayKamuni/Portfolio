import requests
import random
import time
from datetime import datetime

while True:
    # Generate random sample data
    soil_data = {
        "N": 11,
        "P": random.randint(0, 100),
        "K": random.randint(0, 100),
        "pH": round(random.uniform(4.0, 9.0), 2),
        "EC": round(random.uniform(0.1, 5.0), 2),
        "Soil_Moisture": round(random.uniform(10, 50), 2),
        "Soil_Temp": round(random.uniform(15, 40), 2),
        "Atm_Temp": round(random.uniform(20, 45), 2),
        "Atm_Humidity": round(random.uniform(30, 90), 2),
        "rainfall": 11,
    }

    # Send the data to the Flask server
    response = requests.post("https://render-croprecomendation.onrender.com/send_soil_data", json=soil_data)
    
    # Print the response from the server
    print(response.json())

    # Wait for 1 second before sending the next request
    time.sleep(1)
