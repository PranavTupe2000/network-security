import os
import sys
import json

import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
import certifi

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from network_security.utils.exception import NetworkSecurityException

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

ca = certifi.where()

class NetworkDataExtractor():
    
    def __init__(self, database, collection):
        try:
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.database = self.mongo_client[database]
            self.collection=self.database[collection]

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_converter(self, filepath):
        try:
            df = pd.read_csv(filepath)
            df.reset_index(drop=True, inplace=True)
            records = list(json.loads(df.T.to_json()).values())
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records):
        try:
            self.collection.insert_many(records)
            return len(records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == '__main__':
    FILE_PATH = "data\phisingData.csv"
    DATABASE = "NETWORKSECURITY"
    COLLECTION = "NetworkData"
    
    network_data_extractor = NetworkDataExtractor(DATABASE, COLLECTION)
    records = network_data_extractor.csv_to_json_converter(FILE_PATH)
    len_records_inserted = network_data_extractor.insert_data_mongodb(records)
    print(f"Records inserted: {len_records_inserted}")
