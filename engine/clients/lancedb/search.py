import lancedb

from typing import List, Tuple
from dataset_reader.base_reader import Query
from engine.base_client.search import BaseSearcher
from engine.clients.lancedb.config import get_db_config, LANCEDB_COLLECTION_NAME
from engine.clients.lancedb.parser import LanceDBConditionParser

class LanceDBSearcher(BaseSearcher):
    table = None
    parser = LanceDBConditionParser()

    @classmethod
    def init_client(cls, host, distance, connection_params, search_params):
        uri = get_db_config(host, connection_params)
        db  = lancedb.connect(uri)
        cls.table = db.open_table(LANCEDB_COLLECTION_NAME)

    @classmethod
    def search_one(cls, query: Query, top: int) -> List[Tuple[int, float]]:
        """
        1) Build the k-NN + filter "query" by parsing all meta_conditions at once.
        2) If parse() returns an expression, apply it via .where(...).
        3) Run the kNN search on the “vector” column and return (id, score) pairs.
        """
        tbl = cls.table

        expr = cls.parser.parse(query.meta_conditions)
        if expr:
            tbl = tbl.where(expr)

        df = tbl.search(query.vector).limit(top).to_pandas()

        return list(zip(df["id"].tolist(), df["_vector_score"].tolist()))

    @classmethod
    def delete_client(cls):
        pass

