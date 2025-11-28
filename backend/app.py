import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS
from spark_conf import create_spark
from pyspark.sql import Row
from pyspark.ml.recommendation import ALSModel
import os
import random
from datetime import datetime
from pymongo import MongoClient

# Model paths
MODEL_PATH = "als_model"
USER_INDEXER_PATH = "user_indexer.joblib"
ITEM_INDEXER_PATH = "item_indexer.joblib"

app = Flask(__name__)
CORS(app)

# Initialize Spark and model with error handling
try:
    spark = create_spark("ALS-API")
    
    # Check if model files exist
    if os.path.exists(USER_INDEXER_PATH) and os.path.exists(ITEM_INDEXER_PATH):
        user_labels = joblib.load(USER_INDEXER_PATH)
        item_labels = joblib.load(ITEM_INDEXER_PATH)
        
        # Try to load the ALS model, but continue even if it fails
        try:
            als_model = ALSModel.load(MODEL_PATH)
            model_loaded = True
            print("ALS Model loaded successfully")
        except Exception as model_error:
            print(f"ALS model load failed: {model_error}")
            print("Will use fallback recommendations")
            als_model = None
            model_loaded = False
    else:
        model_loaded = False
        user_labels = []
        item_labels = []
        als_model = None
        print(" Indexer files not found")
        
except Exception as e:
    print(f"Initialization failed: {e}")
    model_loaded = False
    spark = None
    user_labels = []
    item_labels = []
    als_model = None

def get_fallback_recommendations(user_id):
    """Fallback recommendations when model fails to load"""
    return [random.randint(1, 100) for _ in range(10)]

def store_recommendation(user_id, recommendations, status):
    """Store recommendations in MongoDB"""
    try:
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client.ecommerce
        db.recommendations.insert_one({
            "user_id": user_id,
            "recommendations": recommendations,
            "status": status,
            "timestamp": datetime.utcnow()
        })
        print(f" Stored recommendations for user {user_id}")
    except Exception as e:
        print(f" Failed to store in MongoDB: {e}")

def get_movie_details(movie_ids):
    """Get movie titles from MongoDB"""
    try:
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client.ecommerce
        movies = []
        for movie_id in movie_ids:
            movie = db.movies.find_one({"item_id": movie_id})
            if movie:
                movies.append({
                    "movie_id": movie_id,
                    "title": movie.get("title", f"Movie {movie_id}"),
                    "genres": movie.get("genres", "Unknown")
                })
            else:
                movies.append({
                    "movie_id": movie_id,
                    "title": f"Movie {movie_id}",
                    "genres": "Unknown"
                })
        return movies
    except Exception as e:
        print(f"Failed to fetch movie details: {e}")
        return [{"movie_id": mid, "title": f"Movie {mid}", "genres": "Unknown"} for mid in movie_ids]

@app.route("/recommend/<user_id>")
def recommend(user_id):
    if not model_loaded or als_model is None:
        recommendations = get_fallback_recommendations(user_id)
        movie_details = get_movie_details(recommendations)
        store_recommendation(user_id, recommendations, "fallback")
        
        return jsonify({
            "user_id": user_id,
            "recommendations": movie_details,
            "status": "fallback_recommendations",
            "message": "Using fallback recommendations - model not loaded"
        })
    
    try:
        user_id_int = int(user_id)
        idx = user_labels.index(user_id_int)
    except (ValueError, AttributeError):
        recommendations = get_fallback_recommendations(user_id)
        movie_details = get_movie_details(recommendations)
        store_recommendation(user_id, recommendations, "user_not_found")
        
        return jsonify({
            "user_id": user_id,
            "recommendations": movie_details,
            "status": "user_not_found_fallback"
        })

    # Generate ALS recommendations
    try:
        user_df = spark.createDataFrame([Row(user=idx)])
        recs = als_model.recommendForUserSubset(user_df, 10).collect()

        if not recs:
            recommendations = get_fallback_recommendations(user_id)
            movie_details = get_movie_details(recommendations)
            store_recommendation(user_id, recommendations, "no_als_recommendations")
            
            return jsonify({
                "user_id": user_id,
                "recommendations": movie_details,
                "status": "no_als_recommendations_fallback"
            })

        rec_list = recs[0]["recommendations"]
        product_indices = [r["item"] for r in rec_list]
        product_ids = [item_labels[i] for i in product_indices]
        movie_details = get_movie_details(product_ids)
        
        store_recommendation(user_id, product_ids, "als_recommendations")

        return jsonify({
            "user_id": user_id,
            "recommendations": movie_details,
            "status": "als_recommendations",
            "count": len(movie_details)
        })
        
    except Exception as e:
        print(f" Recommendation error: {e}")
        recommendations = get_fallback_recommendations(user_id)
        movie_details = get_movie_details(recommendations)
        store_recommendation(user_id, recommendations, "error")
        
        return jsonify({
            "user_id": user_id,
            "recommendations": movie_details,
            "status": "error_fallback",
            "message": str(e)
        })

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model_loaded,
        "spark_ready": spark is not None,
        "user_count": len(user_labels) if user_labels else 0,
        "item_count": len(item_labels) if item_labels else 0,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/recommend/batch", methods=["POST"])
def batch_recommend():
    """Batch recommendations for multiple users"""
    try:
        user_ids = request.json.get("user_ids", [])
        results = []
        
        for user_id in user_ids[:10]: 
            results.append({
                "user_id": user_id,
                "recommendations": get_fallback_recommendations(user_id)
            })
        
        return jsonify({
            "batch_results": results,
            "total_users": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    status = "model_loaded" if model_loaded else "fallback_mode"
    return jsonify({
        "message": "🎬 Movie Recommendation API",
        "status": status,
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend/<user_id>",
            "batch": "/recommend/batch (POST)"
        },
        "database": "MongoDB integration ready"
    })

if __name__ == "__main__":
    print(" Starting Flask Server...")
    print("Health check: http://localhost:5000/health")
    print("Recommendations: http://localhost:5000/recommend/1")
    app.run(host="0.0.0.0", port=5000, debug=True)