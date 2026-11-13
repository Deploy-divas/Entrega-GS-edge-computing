import unittest
from types import SimpleNamespace

from bson import ObjectId

from app.schemas import CriarLeitura
from app.services import registrar_leitura


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
    #tag_reconhecida_retorna_audio
    async def teste_tag_reconhecida_retorna_audio(self):
        item = {
            "_id": ObjectId(),
            "tag_id": "04-A1-B2",
            "nome": "Caixa de chá",
            "audio_descricao": "Chá de camomila.",
        }
        readings = FakeCollection()
        db = SimpleNamespace(products=FakeCollection(item), readings=readings)

        result = await registrar_leitura(db, CriarLeitura(tag_id="04-a1-b2"))

        self.assertEqual(result["status"], "encontrada")
        self.assertEqual(result["nome"], "Caixa de chá")
        self.assertEqual(result["audio_descricao"], "Chá de camomila.")
        self.assertEqual(readings.inserted["item_id"], item["_id"])

    async def teste_tag_desconhecida_salvando(self):
        readings = FakeCollection()
        db = SimpleNamespace(products=FakeCollection(), readings=readings)

        result = await registrar_leitura(db, CriarLeitura(tag_id="unknown-tag"))

        self.assertEqual(result["status"], "desconhecida")
        self.assertIsNone(result["item_id"])
        self.assertIsNone(result["audio_descricao"])
        self.assertEqual(readings.inserted["tag_id"], "UNKNOWN-TAG")


if __name__ == "__main__":
    unittest.main()
