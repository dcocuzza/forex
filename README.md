# forex

# Requirements

* Docker (Desktop on Windows)
* Docker Compose

# Start Project

1. Clone the project repository:
    ```https://github.com/dcocuzza/forex.git ```
2. Go to: kafka/setup and run this command:  
    ``` wget https://dlcdn.apache.org/kafka/3.4.0/kafka_2.13-3.4.0.tgz ```
3. Move to root directory called forex and run these commands:  
    - ``` docker-compose -f forex.yml build ```  
    - ``` docker-compose -f forex.yml up ```  
4. To view data:  
    - Go to: ``` http://locahost:5601 ```    
    - At the home page click on: ``` Stack Management > Saved Object ```  
    - Import these file: ``` kibana/export.ndjson ``` and ``` kibana/tempo.ndjson ```