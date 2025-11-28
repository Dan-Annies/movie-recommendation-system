import joblib
import sys 
import os
from pyspark.sql import functions as F
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from spark_conf import create_spark 

# Model paths
MODEL_PATH = "als_model"
USER_INDEXER_PATH = "user_indexer.joblib"
ITEM_INDEXER_PATH = "item_indexer.joblib"

def train_model():
    spark = create_spark('ALS-Train')

    try:
        print("Loading ratings data from CSV...")
        ratings = (
            spark.read.format("csv")
            .option("header", "true") 
            .option("inferSchema", "true")
            .load("ratings.csv") 
        )
        
        print(f"Loaded {ratings.count():,} ratings")
        print(f"Unique users: {ratings.select('user_id').distinct().count():,}")
        print(f"Unique items: {ratings.select('item_id').distinct().count():,}")

        # Data preprocessing
        user_indexer = StringIndexer(inputCol='user_id', outputCol='user')
        item_indexer = StringIndexer(inputCol='item_id', outputCol='item')

        print("Fitting indexers...")
        user_indexer_model = user_indexer.fit(ratings)
        item_indexer_model = item_indexer.fit(ratings)

        print("Transforming data...")
        indexed_data = user_indexer_model.transform(ratings)
        indexed_data = item_indexer_model.transform(indexed_data)

        # Prepare final dataset
        final_data = indexed_data.select(
            F.col('user').cast('integer').alias('user'),
            F.col('item').cast('integer').alias('item'),
            F.col('rating').cast('float').alias('rating')
        ).cache()

        # Train-test split
        train, test = final_data.randomSplit([0.8, 0.2], seed=42)
        print(f"Training samples: {train.count():,}")
        print(f"Test samples: {test.count():,}")

        # ALS Model configuration
        als = ALS(
            userCol='user',
            itemCol='item',
            ratingCol='rating',
            nonnegative=True,
            rank=10,
            maxIter=10,
            regParam=0.1,
            coldStartStrategy='drop',
            seed=42
        )

        print("Starting ALS model training...")
        model = als.fit(train)
        print("ALS model training complete.")

        # Evaluation
        print("Evaluating model...")
        predictions = model.transform(test)
        evaluator = RegressionEvaluator(
            metricName='rmse', 
            labelCol='rating', 
            predictionCol='prediction'
        )
        rmse = evaluator.evaluate(predictions)
        print(f'Model RMSE: {rmse:.4f}')

        # SKIP MODEL SAVING due to Windows Hadoop issues
        print("Skipping model save due to Windows Hadoop compatibility issues")
        print("The model trained successfully but cannot be saved on Windows")
        print("System will use fallback recommendations")

        print("Saving indexers...")
        joblib.dump(user_indexer_model.labels, USER_INDEXER_PATH)
        joblib.dump(item_indexer_model.labels, ITEM_INDEXER_PATH)
        print("Indexers saved successfully!")
        
        # Create training complete flag
        with open("training_complete.flag", "w") as f:
            f.write(f"Training completed at: {os.path.basename(MODEL_PATH)}\nRMSE: {rmse:.4f}\nNote: Model not saved due to Windows Hadoop issues")
        
        print("Training completed successfully! Using fallback mode.")
        return True
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        spark.stop()
        print("Spark session stopped.")

if __name__ == "__main__":
    success = train_model()
    sys.exit(0 if success else 1)