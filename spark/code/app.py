from __future__ import print_function

import sys
import pandas as pd
import json
import datetime

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame

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
    print(exchange_rate)
   

    
  
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