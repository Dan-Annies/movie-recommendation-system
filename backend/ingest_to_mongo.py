import pandas as pd
from pymongo import MongoClient

MONGO_URI = "mongodb://127.0.0.1:27017"
DB_NAME = "ecommerce"

def ingest(ratings_csv='ratings.csv', movies_csv='movies.csv'):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    try:
        print("Loading data from CSV files...")
        ratings = pd.read_csv(ratings_csv)
        movies = pd.read_csv(movies_csv)

        print(f"Ratings: {len(ratings):,} records")
        print(f" Movies: {len(movies):,} records")

        # Clear existing collections
        print(" Clearing existing collections...")
        db.ratings.drop()
        db.movies.drop()
        db.recommendations.drop()

        # Insert new data
        print(" Inserting ratings...")
        db.ratings.insert_many(ratings.to_dict('records'))
        
        print(" Inserting movies...")
        db.movies.insert_many(movies.to_dict('records'))

        # Create indexes for better performance
        print(" Creating indexes...")
        db.ratings.create_index("user_id")
        db.ratings.create_index("item_id")
        db.movies.create_index("item_id")
        db.recommendations.create_index("user_id")
        db.recommendations.create_index("timestamp")

        # Verify insertion
        ratings_count = db.ratings.count_documents({})
        movies_count = db.movies.count_documents({})

        print(f" Successfully ingested {ratings_count:,} ratings")
        print(f" Successfully ingested {movies_count:,} movies")
        print(" MongoDB data ingestion complete!")

    except Exception as e:
        print(f" Error during ingestion: {e}")
        raise e

if __name__ == '__main__':
    ingest()