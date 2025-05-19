import lancedb
import pyarrow as pa

from benchmark.dataset import Dataset
from engine.base_client import IncompatibilityError
from engine.base_client.configure import BaseConfigurator
from engine.clients.lancedb.config import get_db_config, LANCEDB_COLLECTION_NAME


class LanceDBConfigurator(BaseConfigurator):
    def __init__(self, host, collection_params, connection_params):
        super().__init__(host, collection_params, connection_params)
        uri = get_db_config(host, connection_params)
        self.db = lancedb.connect(uri)

    def clean(self):
        self.db.drop_table(LANCEDB_COLLECTION_NAME, ignore_missing=True)

    def recreate(self, dataset: Dataset, collection_params):
        if not dataset.config.vector_size:
            raise IncompatibilityError("Dataset has no vector_size")

        fields = [
            pa.field("id", pa.int64()),
            pa.field(
                "vector",
                pa.list_(pa.float32(), list_size=dataset.config.vector_size),
            ),
        ]

        for name, typ in (dataset.config.schema or {}).items():
            if typ == "int":
                fields.append(pa.field(name, pa.int64()))
            elif typ == "float":
                fields.append(pa.field(name, pa.float32()))
            elif typ in ("keyword", "text"):
                fields.append(pa.field(name, pa.string()))
            else:
                raise IncompatibilityError(f"Unsupported schema type: {typ}")

        full_schema = pa.schema(fields)
        self.table = self.db.create_table(
            LANCEDB_COLLECTION_NAME,
            schema=full_schema,
            mode="overwrite"
        )

    def delete_client(self):
        pass
