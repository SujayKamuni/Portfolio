from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Initialize Flask app, serving static files from the 'frontend' directory
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app) # Enable Cross-Origin Resource Sharing for the app

# Route for the root URL, serving Homepage.html (your portfolio webpage)
@app.route("/")
def home():
    # This route now serves 'Homepage.html' as the main entry point
    return send_from_directory("frontend", "Homepage.html")

# Route for Homepage.html (can still be accessed directly)
@app.route("/Homepage.html")
def home_page():
    return send_from_directory("frontend", "Homepage.html")

# Route for serving static files (e.g., CSS, JS, images) from the 'frontend/static' directory
@app.route("/static/<path:filename>")
def static_files(filename):
    # Ensure the 'static' folder exists within 'frontend'
    # For example, if your CSS is in 'frontend/static/css/style.css',
    # it would be accessed via '/static/css/style.css'
    return send_from_directory("frontend/static", filename)

# Main entry point for running the Flask application
if __name__ == "__main__":
    # Run the app on all available network interfaces (0.0.0.0) on port 5003 in debug mode
    app.run(host="0.0.0.0", port=5003, debug=True)
