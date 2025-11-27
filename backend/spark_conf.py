from pyspark.sql import SparkSession
from pyspark import SparkConf

def create_spark(app_name='EcommerceRec'):
    conf = SparkConf()
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    conf.set("spark.driver.memory", "2g")
    conf.set("spark.executor.memory", "2g")
    conf.set("spark.network.timeout", "600s")

    spark = SparkSession.builder \
        .appName(app_name) \
        .config(conf=conf) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    return spark