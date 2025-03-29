from flask import Flask, send_from_directory, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

model_filename = "RandomForest_Model.pkl"  
with open(model_filename, "rb") as file:
    model = pickle.load(file)
soil_data = []


excel_file = "crop_data.xlsx"


@app.route("/")
def home():
    return send_from_directory("frontend", "Sensor_data.html")

@app.route("/crop.html")
def crop_page():
    return send_from_directory("frontend", "index.html")

@app.route("/Homepage.html")
def home_page():
    return send_from_directory("frontend", "Homepage.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend/static", filename)

@app.route('/download_excel')
def download_excel():
    return send_file(excel_file, as_attachment=True)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        features = [
            data["N"], data["P"], data["K"],
            data["pH"], data["EC"], data["Soil_Moisture"],
            data["Soil_Temp"], data["Atm_Temp"], data["Atm_Humidity"], data["rainfall"]
        ]

        features_array = np.array([features])
        prediction = model.predict(features_array)[0]

        save_data_to_excel(data, prediction)

        return jsonify({"recommended_crop": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def save_data_to_excel(data, prediction):
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Nitrogen (N)": data["N"],
        "Phosphorus (P)": data["P"],
        "Potassium (K)": data["K"],
        "pH Level": data["pH"],
        "EC": data["EC"],
        "Soil Moisture": data["Soil_Moisture"],
        "Soil Temperature": data["Soil_Temp"],
        "Atmospheric Temperature": data["Atm_Temp"],
        "Atmospheric Humidity": data["Atm_Humidity"],
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

@app.route("/send_soil_data", methods=["POST"])
def receive_soil_data():
    try:
        data = request.json
        soil_data.append(data)  
        print("Received Soil Data:", data)
        return jsonify({"message": "Data received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/get_excel_data", methods=["GET"])
def get_excel_data():
    """Retrieve data from Excel file."""
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        return jsonify({"data": df.to_dict(orient="records")})
    return jsonify({"error": "No data found"}), 404


@app.route("/get_soil_data", methods=["GET"])
def get_soil_data():
    """Send latest soil data to webpage."""
    if soil_data:
        return jsonify(soil_data[-1])  
    return jsonify({"error": "No data available"}), 404

irrigation_status = {
    "soil_moisture": 0,
    "water_pump": "OFF",
    "nitrogen_level": 0,
    "nitrogen_pump": "OFF"
}

@app.route("/update_irrigation_status", methods=["POST"])
def update_irrigation_status():
    global irrigation_status
    data = request.json

    irrigation_status["soil_moisture"] = data.get("soil_moisture", 0)
    irrigation_status["water_pump"] = data.get("water_pump", "OFF")
    irrigation_status["nitrogen_level"] = data.get("nitrogen_level", 0)
    irrigation_status["nitrogen_pump"] = data.get("nitrogen_pump", "OFF")

    return jsonify({"message": "Irrigation status updated!"})

@app.route("/get_irrigation_status", methods=["GET"])
def get_irrigation_status():
    return jsonify(irrigation_status)

selected_crop = ""  # Default crop

@app.route('/get_selected_crop', methods=['GET'])
def get_selected_crop():
    return jsonify({"selected_crop": selected_crop})

@app.route('/set_selected_crop', methods=['POST'])
def set_selected_crop():
    global selected_crop
    data = request.json
    if "crop" in data:
        selected_crop = data["crop"]
        return jsonify({"message": f"Crop updated to {selected_crop}"})
    return jsonify({"error": "Invalid request"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
