to start SPARK-CITY.PY
docker exec -it vechiledataanalysisrealtimekafka-spark-aws-spark-master-1 spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 jobs/spark-city.py



For Main.py
python jobs/main.py

To create docker with AWS CLI image
docker run -it --rm amazon/aws-cli
docker rm -f aws-cli/docker run -it --name aws-cli --entrypoint sh amazon/aws-cli --> to enter into docker container
aws configure





Kafka Consumer:
docker run -it --rm --network vechiledataanalysisrealtimekafka-spark-aws_datamasterylab confluentinc/cp-kafka:latest kafka-console-consumer --bootstrap-server broker:29092 --topic emergency_data --from-beginning