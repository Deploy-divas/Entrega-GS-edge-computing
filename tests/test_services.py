import unittest
from types import SimpleNamespace

from bson import ObjectId

from app.schemas import ReadingCreate
from app.services import register_reading


class FakeCollection:
    def __init__(self, document=None):
        self.document = document
        self.inserted = None

    async def find_one(self, query):
        return self.document if self.document and query["tag_id"] == self.document["tag_id"] else None

    async def insert_one(self, document):
        self.inserted = document
        return SimpleNamespace(inserted_id=ObjectId())


class ReadingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_known_tag_returns_product_audio_and_saves_snapshot(self):
        product = {
            "_id": ObjectId(),
            "tag_id": "04-A1-B2",
            "name": "Caixa de chá",
            "audio_description": "Chá de camomila.",
        }
        readings = FakeCollection()
        db = SimpleNamespace(products=FakeCollection(product), readings=readings)

        result = await register_reading(db, ReadingCreate(tag_id="04-a1-b2"))

        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["product_name"], "Caixa de chá")
        self.assertEqual(result["audio_description"], "Chá de camomila.")
        self.assertEqual(readings.inserted["product_id"], product["_id"])

    async def test_unknown_tag_is_still_saved_and_reported(self):
        readings = FakeCollection()
        db = SimpleNamespace(products=FakeCollection(), readings=readings)

        result = await register_reading(db, ReadingCreate(tag_id="unknown-tag"))

        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["product_id"])
        self.assertIsNone(result["audio_description"])
        self.assertEqual(readings.inserted["tag_id"], "UNKNOWN-TAG")


if __name__ == "__main__":
    unittest.main()
