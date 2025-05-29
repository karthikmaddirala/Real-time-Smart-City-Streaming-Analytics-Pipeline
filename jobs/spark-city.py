from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col, regexp_replace, split, trim
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType
from pyspark.sql.functions import col, max as spark_max, lit

from config import configuration

def main():
    spark = SparkSession.builder.appName("SmartCityStreaming") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0," 
                "org.apache.hadoop:hadoop-aws:3.3.1," 
                "com.amazonaws:aws-java-sdk:1.11.469") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY')) \
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY')) \
        .config('spark.hadoop.fs.s3a.aws.credentials.provider',
                'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
        .getOrCreate()

    spark.sparkContext.setLogLevel('WARN')

    def process_location(df):
        df = df.withColumn("location", regexp_replace("location", "[()]", ""))
        df = df.withColumn("latitude", trim(split(col("location"), ",").getItem(0)).cast("double"))
        df = df.withColumn("longitude", trim(split(col("location"), ",").getItem(1)).cast("double"))
        return df.drop("location")

    def streamWriter(input: DataFrame, checkpointFolder, output):
        return (input.writeStream
                .format('parquet')
                .option('checkpointLocation', checkpointFolder)
                .option('path', output)
                .outputMode('append')
                .trigger(processingTime="2 minutes")
                .start())

    # Schemas
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True),
    ])

    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicleType", StringType(), True)
    ])

    trafficSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("cameraId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("snapshot", StringType(), True)
    ])

    weatherSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("airQualityIndex", DoubleType(), True),
    ])

    emergencySchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("incidentId", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True),
    ])

    def read_kafka_topic(topic, schema):
        return (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', 'broker:29092')
                .option('subscribe', topic)
                .option('startingOffsets', 'earliest')
                .load()
                .selectExpr('CAST(value AS STRING)')
                .select(from_json(col('value'), schema).alias('data'))
                .select('data.*')
                .withWatermark('timestamp', '2 minutes'))




    def write_latest(batch_df, batch_id):
        print(f"[Batch {batch_id}] Processing started...")

        if not batch_df.isEmpty():
        # Get the latest row by timestamp
            latest_row = batch_df.orderBy(col("timestamp").desc()).limit(1).collect()[0]

        # Print selected fields from the row
            print(f"[Latest] Device ID: {latest_row['deviceId']}, Timestamp: {latest_row['timestamp']}")
            print(f"         Location: ({latest_row['latitude']}, {latest_row['longitude']}), Speed: {latest_row['speed']} km/h")
            print(f"         Weather: {latest_row['weatherCondition']} @ {latest_row['temperature']}°C")
            print(f"         Emergency: {latest_row['emergency']} ({latest_row['emergencyStatus']})")
        else:
            print(f"[Batch {batch_id}] No data in this batch.")


    # Read and process streams
    vehicleDF = process_location(read_kafka_topic('vehicle_data', vehicleSchema)).alias('vehicle')
    weatherDF = process_location(read_kafka_topic('weather_data', weatherSchema)).alias('weather')
    emergencyDF = process_location(read_kafka_topic('emergency_data', emergencySchema)).alias('emergency')
    gpsDF = read_kafka_topic('gsp_data', gpsSchema).alias('gps')
    trafficDF = process_location(read_kafka_topic('traffic_data', trafficSchema)).alias('traffic')

    # Updated join using exact timestamp match (since timestamps are aligned)
    joinedDF = vehicleDF.join(weatherDF, vehicleDF.timestamp == weatherDF.timestamp, "inner") \
        .join(emergencyDF, vehicleDF.timestamp == emergencyDF.timestamp, "inner") \
        .select(
            col("vehicle.deviceId").alias("deviceId"),
            col("vehicle.timestamp").alias("timestamp"),
            col("vehicle.latitude"),
            col("vehicle.longitude"),
            col("vehicle.speed"),
            col("vehicle.direction"),
            col("weather.temperature"),
            col("weather.weatherCondition"),
            col("emergency.type").alias("emergency"),
            col("emergency.status").alias("emergencyStatus")
        )

    # Write all streams
    query_vehicle = streamWriter(vehicleDF, 's3a://spark-streaming-data/checkpoints/vehicle_data', 's3a://spark-streaming-data/data/vehicle_data')
    query_gps = streamWriter(gpsDF, 's3a://spark-streaming-data/checkpoints/gps_data', 's3a://spark-streaming-data/data/gps_data')
    query_traffic = streamWriter(trafficDF, 's3a://spark-streaming-data/checkpoints/traffic_data', 's3a://spark-streaming-data/data/traffic_data')
    query_emergency = streamWriter(emergencyDF, 's3a://spark-streaming-data/checkpoints/emergency_data', 's3a://spark-streaming-data/data/emergency_data')
    query_weather = streamWriter(weatherDF, 's3a://spark-streaming-data/checkpoints/weather_data', 's3a://spark-streaming-data/data/weather_data')
    query_processed = streamWriter(joinedDF, 's3a://spark-streaming-data/checkpoints/enriched_data', 's3a://spark-streaming-data/data/enriched_data')

    queries = [query_vehicle, query_gps, query_traffic, query_emergency, query_weather, query_processed]

# This waits until any query fails or you press Ctrl+C
    for q in queries:
        q.awaitTermination()

if __name__ == "__main__":
    main()
