import lancedb
import pyarrow as pa

from benchmark.dataset import Dataset
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
        schema = pa.schema([
            pa.field("id", pa.int64()),
            pa.field("vector", pa.list_(pa.float32(), list_size=dataset.config.vector_size))
        ])
        self.table = self.db.create_table(
            LANCEDB_COLLECTION_NAME,
            schema=schema,
            mode="overwrite"
        )

    def delete_client(self):
        pass

