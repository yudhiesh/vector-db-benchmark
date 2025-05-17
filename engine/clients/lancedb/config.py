from typing import Optional, Dict

LANCEDB_COLLECTION_NAME = os.getenv("LANCEDB_COLLECTION_NAME", "benchmark")

def get_db_config(host: Optional[str], connection_params: Dict) -> str:
    """
    Build a LanceDB connection URI.
    - For local FS: e.g. "data/mydb"
    - For S3 + DDB (LocalStack or AWS): "s3+ddb://bucket/path?ddbTableName=commit_table"
    """
    # Base path or bucket
    base = connection_params.get("uri") or f"data/{host or 'lancedb'}"
    if connection_params.get("use_s3"):
        bucket = connection_params["bucket"]
        ddb = connection_params.get("ddb_table_name", "lancedb_commit")
        return f"s3+ddb://{bucket}/{base}?ddbTableName={ddb}"
    return base

