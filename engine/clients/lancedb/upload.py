import lancedb

from engine.base_client.upload import BaseUploader
from engine.base_client import IncompatibilityError
from engine.base_client.distances import Distance
from engine.clients.lancedb.config import get_db_config, LANCEDB_COLLECTION_NAME


class LanceDBUploader(BaseUploader):
    DISTANCE_MAPPING = {
        Distance.L2: "l2",
        Distance.COSINE: "cosine",
        Distance.DOT: "dot",
    }

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        uri = get_db_config(host, connection_params)
        db = lancedb.connect(uri)
        cls.table = db.open_table(LANCEDB_COLLECTION_NAME)

    @classmethod
    def upload_batch(cls, batch):
        records = [{"id": rec.id, "vector": rec.vector} for rec in batch]
        cls.table.add(records)

    @classmethod
    def post_upload(cls, distance):
        metric = cls.DISTANCE_MAPPING.get(distance)
        if metric is None:
            raise IncompatibilityError(f"Unsupported metric: {distance}")
        cls.table.create_index(metric=metric)
        cls.table.wait_for_index()
        return {}

    @classmethod
    def delete_client(cls):
        pass
