import pandas as pd
import os

BASE = "ml-100k"   # extracted folder

# 1. Convert u.data → ratings.csv
ratings_cols = ["user_id", "item_id", "rating", "timestamp"]
ratings = pd.read_csv(os.path.join(BASE, "u.data"), sep="\t", names=ratings_cols)
ratings.to_csv("ratings.csv", index=False)

# 2. Convert u.item → movies.csv
movies_cols = [
    "item_id", "title", "release_date", "video_release_date",
    "imdb_url"
] + [f"genre_{i}" for i in range(19)]

movies = pd.read_csv(os.path.join(BASE, "u.item"), sep="|", names=movies_cols, encoding="latin-1")
movies.to_csv("movies.csv", index=False)

print("Conversion complete: ratings.csv and movies.csv created.")
