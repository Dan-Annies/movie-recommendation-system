# simple_app.py
from flask import Flask, jsonify
from flask_cors import CORS  # Add this line
import random

app = Flask(__name__)
CORS(app)  # Add this line

# ... rest of your code

# Mock recommendations for now
def get_mock_recommendations(user_id):
    # Return some mock movie IDs
    return [random.randint(1, 100) for _ in range(10)]

@app.route("/recommend/<user_id>")
def recommend(user_id):
    recommendations = get_mock_recommendations(user_id)
    return jsonify({
        "user_id": user_id,
        "recommendations": recommendations,
        "status": "mock_data"  # So you know it's not real recommendations
    })

@app.route("/")
def home():
    return jsonify({"message": "Recommendation API is running!", "status": "mock_mode"})

if __name__ == "__main__":
    print("Starting Flask server with mock data...")
    print("Go to: http://localhost:5000/recommend/1")
    app.run(host="0.0.0.0", port=5000, debug=True)