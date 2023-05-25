FROM jupyter/pyspark-notebook:spark-3.4.0

RUN pip3 install pyspark numpy elasticsearch datetime

WORKDIR /app

COPY ./code .

ENTRYPOINT ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0", "--master", "local[*]", "app.py"]