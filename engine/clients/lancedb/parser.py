import json
from typing import Optional
from engine.base_client import IncompatibilityError
from engine.base_client.parser import BaseConditionParser, FieldValue

class LanceDBConditionParser(BaseConditionParser):
    def build_condition(self, and_subfilters, or_subfilters) -> Optional[str]:
        clauses = []
        if or_subfilters:
            clauses.append(f"( {' OR '.join(or_subfilters)} )")
        if and_subfilters:
            clauses.append(f"( {' AND '.join(and_subfilters)} )")
        return " AND ".join(clauses) if clauses else None

    def build_exact_match_filter(self, field_name: str, value: FieldValue) -> str:
        return f"{field_name} = {json.dumps(value)}"

    def build_range_filter(self, field_name, lt, gt, lte, gte):
        parts = []
        if lt  is not None: parts.append(f"{field_name} < {lt}")
        if gt  is not None: parts.append(f"{field_name} > {gt}")
        if lte is not None: parts.append(f"{field_name} <= {lte}")
        if gte is not None: parts.append(f"{field_name} >= {gte}")
        return " AND ".join(parts)

    def build_geo_filter(self, *args, **kwargs):
        raise IncompatibilityError

