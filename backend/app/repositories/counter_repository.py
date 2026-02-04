from pymongo import ReturnDocument

class CounterRepository:
    def __init__(self, db):
        self.collection = db["counters"]

    def get_next_sequence(self, name: str) -> int:
        counter = self.collection.find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return counter["seq"]
