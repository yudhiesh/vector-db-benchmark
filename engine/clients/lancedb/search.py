from enum import Enum
import lancedb

from typing import Any, List, Tuple
import pandas as pd
from dataset_reader.base_reader import Query
from engine.base_client.search import BaseSearcher
from engine.clients.lancedb.config import get_db_config, LANCEDB_COLLECTION_NAME
from engine.clients.lancedb.parser import LanceDBConditionParser


class FilterMethod(str, Enum):
    PREFILTER = "prefilter"
    POSTFILTER = "postfilter"


class LanceDBSearcher(BaseSearcher):
    table = None
    parser = LanceDBConditionParser()

    @classmethod
    def get_mp_start_method(cls) -> str:
        # Refer to https://lancedb.github.io/lancedb/faq/#does-lancedb-support-concurrent-operations
        return "spawn"

    @classmethod
    def init_client(cls, host, distance, connection_params, search_params):
        uri = get_db_config(host, connection_params)
        db = lancedb.connect(uri)
        cls.table = db.open_table(LANCEDB_COLLECTION_NAME)
        cls.search_params = search_params

    @classmethod
    def search_one(cls, query: Query, top: int) -> List[Tuple[int, float]]:
        """
        1) Build the k-NN + filter "query" by parsing all meta_conditions at once.
        2) If parse() returns an expression, apply it via .where(...).
        3) Run the kNN search on the “vector” column and return (id, score) pairs.
        """
        tbl = cls.table

        expr = cls.parser.parse(query.meta_conditions)
        filter_method_spec = cls.search_params.get("filter_method")
        if expr and filter_method_spec:
            filter_method = FilterMethod(filter_method_spec)
            df = cls.build_filter_expr(tbl, filter_method, query, top, expr)

        else:
            df = tbl.search(query.vector).limit(top).to_pandas()

        return list(zip(df["id"].tolist(), df["_distance"].tolist()))

    @classmethod
    def delete_client(cls):
        pass

    @classmethod
    def build_filter_expr(
        cls,
        table: lancedb.table.Table,
        filter_method: FilterMethod,
        query: Query,
        top: int,
        filter_expr: Any,
    ) -> pd.DataFrame:
        if FilterMethod.PREFILTER == filter_method:
            return (
                table.where(filter_expr, prefilter=True)
                .search(query.vector)
                .limit(top)
                .to_pandas()
            )
        if FilterMethod.POSTFILTER == filter_method:
            return table.where(filter_expr).search(query.vector).limit(top).to_pandas()
