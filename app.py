from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask import Flask, send_file
import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Load the trained model
model_filename = "RandomForest.pkl"  
with open(model_filename, "rb") as file:
    model = pickle.load(file)

# Store received soil data
soil_data = []

# Excel file path
excel_file = "crop_data.xlsx"

# Serve Home Page
@app.route("/")
def home():
    return send_from_directory("frontend", "Sensor_data.html")

# Serve Crop Recommendation Page
@app.route("/crop.html")
def crop_page():
    return send_from_directory("frontend", "index.html")

@app.route("/Homepage.html")
def Home_page():
    return send_from_directory("frontend", "Homepage.html")

# Serve Static Files (CSS, JS, Images)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend/static", filename)

#sending excel file for downloading
@app.route('/download_excel')
def download_excel():
    return send_file(excel_file, as_attachment=True)

# Predict Crop Recommendation
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        features = [
            data["N"], data["P"], data["K"],
            data["temperature"], data["humidity"],
            data["ph"], data["rainfall"]
        ]

        # Convert to numpy array and make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]

        # Save to Excel
        save_data_to_excel(data, prediction)

        return jsonify({"recommended_crop": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Save Data to Excel
def save_data_to_excel(data, prediction):
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Nitrogen (N)": data["N"],
        "Phosphorus (P)": data["P"],
        "Potassium (K)": data["K"],
        "Temperature": data["temperature"],
        "Humidity": data["humidity"],
        "pH Level": data["ph"],
        "Rainfall": data["rainfall"],
        "Recommended Crop": prediction
    }

    df_new = pd.DataFrame([new_entry])

    if not os.path.exists(excel_file):
        df_new.to_excel(excel_file, index=False)
    else:
        df_existing = pd.read_excel(excel_file)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(excel_file, index=False)

# Receive Soil Data from raspberry pi
@app.route("/send_soil_data", methods=["POST"])
def receive_soil_data():
    try:
        data = request.json
        soil_data.append(data)  # Store latest data
        print("Received Soil Data:", data)
        return jsonify({"message": "Data received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Retrieve Data from Excel
@app.route("/get_excel_data", methods=["GET"])
def get_excel_data():
    """Retrieve data from Excel file."""
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        return jsonify({"data": df.to_dict(orient="records")})
    return jsonify({"error": "No data found"}), 404

# Send Latest Soil Data to Webpage
@app.route("/get_soil_data", methods=["GET"])
def get_soil_data():
    """Send latest soil data to webpage."""
    if soil_data:
        return jsonify(soil_data[-1])  # Return latest data
    return jsonify({"error": "No data available"}), 404

# Run the Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1000, debug=True)
