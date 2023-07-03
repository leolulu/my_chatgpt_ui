from typing import Optional

import pymongo
from pymongo import MongoClient
from retrying import retry


class MongoUtil:
    TIMEOUT = 3

    def __init__(self, host, port, username, password, database="default") -> None:
        self.client = MongoClient(host=host, port=port, username=username, password=password)
        self.db = self.client[database]

    def set_collection(self, collection):
        self.collection = self.db[collection]

    @retry
    def insert_one(self, data: dict):
        with pymongo.timeout(MongoUtil.TIMEOUT):
            return self.collection.insert_one(data)

    @retry
    def find_one(self, data: dict):
        with pymongo.timeout(MongoUtil.TIMEOUT):
            return self.collection.find_one(data)

    @retry
    def delete_one(self, data: dict):
        with pymongo.timeout(MongoUtil.TIMEOUT):
            return self.collection.delete_one(data)

    @retry
    def find_many(self, data: Optional[dict] = None):
        with pymongo.timeout(MongoUtil.TIMEOUT):
            return self.collection.find(data)
