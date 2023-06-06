from __future__ import print_function

import sys
import json
import datetime

from elasticsearch import Elasticsearch
from datetime import datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler

exchange_rates = []
timestp = []

es_index = "eurusd"
es_address = "http://elasticsearch:9200"
es = Elasticsearch(hosts = es_address, verify_certs=False)

response = es.indices.create(index = es_index)

if 'acknowledged' in response:
  if response['acknowledged'] == True:
    print("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])




def linear_regression():
  training_data = spark.createDataFrame([(float(last_refreshed), float(exchange_rate),) for last_refreshed, exchange_rate in zip(timestp, exchange_rates)], ["last_refreshed", "exchange_rate"])
  assembler = VectorAssembler(inputCols=["last_refreshed"], outputCol="features")
  prepared_data = assembler.transform(training_data)

  lr = LinearRegression(featuresCol="features", labelCol="exchange_rate")
  lr_model = lr.fit(prepared_data)

  print("Coefficients: {}".format(lr_model.coefficients))
  print("Intercept: {}".format(lr_model.intercept))

  predictions = lr_model.transform(prepared_data)
  return predictions


id = 0

def elaborate(batch_df: DataFrame, batch_id: int):

  batch_df.show(truncate=False)

  pandasDF = batch_df.select("value").toPandas()
  
  if(pandasDF.empty == False):
    api_response = json.loads(pandasDF['value'][0])
    from_currency_code = api_response['Realtime Currency Exchange Rate']['1. From_Currency Code']
    from_currency_name = api_response['Realtime Currency Exchange Rate']['2. From_Currency Name']
    to_currency_code = api_response['Realtime Currency Exchange Rate']['3. To_Currency Code']
    to_currency_name = api_response['Realtime Currency Exchange Rate']['4. To_Currency Name']
    exchange_rate = api_response['Realtime Currency Exchange Rate']['5. Exchange Rate']
    last_refreshed = api_response['Realtime Currency Exchange Rate']['6. Last Refreshed']
    time_zone = api_response['Realtime Currency Exchange Rate']['7. Time Zone']
    bid_price = api_response['Realtime Currency Exchange Rate']['8. Bid Price']
    ask_price = api_response['Realtime Currency Exchange Rate']['9. Ask Price']
    #print(exchange_rate)


    last_refreshed_numeric = last_refreshed[11:16]
    last_refreshed_numeric = last_refreshed_numeric.replace(":", "")
    last_refreshed_numeric = float(last_refreshed_numeric)

    timestp.append(last_refreshed_numeric)
    exchange_rates.append(exchange_rate)
    
    predictions = linear_regression()
    predictions.show()

    

    prediction_values = predictions.select("exchange_rate", "prediction").collect()
    for row in prediction_values:
      exchange_rate = row["exchange_rate"]
      prediction = row["prediction"]

    print("Exchange Rate: {}, Prediction: {}".format(exchange_rate, prediction))
    print("Valore intero: ", prediction)

    data = datetime.strptime(last_refreshed, "%Y-%m-%d %H:%M:%S")
      
    doc = {
      "timestamp" : data,
      "timestamp_numeric" : int(last_refreshed_numeric),
      "from_currency_name" : from_currency_name,
      "to_currency_name" : to_currency_name,
      "exchange_rate": exchange_rate,
      "prediction": prediction
    }

    global id
    id = id + 1
      
    risp = es.index(index = es_index, id = id, document = doc)
    print(risp['result'])


      
  
sc = SparkContext(appName="PythonStructuredStreamsKafka")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

kafkaServer="kafkaServer:9092"
topic = "eurusd"







# Streaming Query

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafkaServer) \
  .option("subscribe", topic) \
  .load()

df.selectExpr("CAST(timestamp AS STRING)","CAST(value AS STRING)") \
  .writeStream \
  .foreachBatch(elaborate) \
  .start() \
  .awaitTermination()


#df.writeStream \
#  .format("console") \
#  .start() \
#  .awaitTermination()