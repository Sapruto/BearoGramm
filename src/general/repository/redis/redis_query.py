from pydantic import field_validator
from typing import Any, Dict, Optional, List, Tuple, Literal

from ..interfaces.query_interface import QueryInterface
from ...types_var import Fields

class RedisQuery(QueryInterface[Fields]):
    filters: Optional[Dict[Fields, Any]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    order_by: Optional[List[Tuple[Fields, Literal['asc', 'desc']]]] = None

    pattern: Optional[str] = None
    scan_count: Optional[int] = 100

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError(f"Limit must be greater than 0, got {v}")
        return v

    @field_validator('offset')
    @classmethod
    def validate_offset(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError(f"Offset must be greater than or equal to 0, got {v}")
        return v

    @field_validator('order_by')
    @classmethod
    def validate_order_by(cls, v: Optional[List[Tuple[Fields, str]]]) -> Optional[List[Tuple[Fields, str]]]:
        if v:
            allowed_directions = {'asc', 'desc'}
            for idx, (field, direction) in enumerate(v):
                if direction.lower() not in allowed_directions:
                    raise ValueError(
                        f"Direction must be 'asc' or 'desc' (case-insensitive), "
                        f"got '{direction}' at position {idx} for field '{field}'"
                    )
                v[idx] = (field, direction.lower())
        return v

    @field_validator('scan_count')
    @classmethod
    def validate_scan_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError(f"Scan count must be greater than 0, got {v}")
        return v

    def add_filter(self, field: Fields, value: Any) -> 'RedisQuery[Fields]':
        if self.filters is None:
            self.filters = {}
        self.filters[field] = value
        return self

    def remove_filter(self, field: Fields) -> 'RedisQuery[Fields]':
        if self.filters and field in self.filters:
            del self.filters[field]
        return self

    def clear_filters(self) -> 'RedisQuery[Fields]':
        self.filters = None
        return self

    def add_order_by(self, field: Fields, direction: str = 'asc') -> 'RedisQuery[Fields]':
        if self.order_by is None:
            self.order_by = []
        direction_lower = direction.lower()
        if direction_lower not in {'asc', 'desc'}:
            raise ValueError(f"Direction must be 'asc' or 'desc', got '{direction}'")
        self.order_by.append((field, direction_lower))
        return self

    def clear_order_by(self) -> 'RedisQuery[Fields]':
        self.order_by = None
        return self

    def set_pagination(self, limit: int, offset: int = 0) -> 'RedisQuery[Fields]':
        self.limit = limit
        self.offset = offset
        return self

    def set_pattern(self, pattern: str) -> 'RedisQuery[Fields]':
        self.pattern = pattern
        return self

    def reset(self) -> 'RedisQuery[Fields]':
        self.filters = None
        self.limit = None
        self.offset = None
        self.order_by = None
        self.pattern = None
        return self