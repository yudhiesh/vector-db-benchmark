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
    INDEX_NAME = "vector_idx"

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        uri = get_db_config(host, connection_params)
        db = lancedb.connect(uri)
        cls.table = db.open_table(LANCEDB_COLLECTION_NAME)

    @classmethod
    def upload_batch(cls, batch):
        records = []
        for rec in batch:
            rec_dict = {
                "id": rec.id,
                "vector": rec.vector,
            }

            if hasattr(rec, "metadata") and isinstance(rec.metadata, dict):
                rec_dict.update(rec.metadata)

            else:
                for key, val in rec.__dict__.items():
                    if key not in ("id", "vector"):
                        rec_dict[key] = val

            records.append(rec_dict)

        cls.table.add(records)

    @classmethod
    def post_upload(cls, distance):
        metric = cls.DISTANCE_MAPPING.get(distance)
        if metric is None:
            raise IncompatibilityError(f"Unsupported metric: {distance}")
        cls.table.create_index(metric=metric)
        cls.table.wait_for_index([cls.INDEX_NAME])
        return {}

    @classmethod
    def delete_client(cls):
        pass
