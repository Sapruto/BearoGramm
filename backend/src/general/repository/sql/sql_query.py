from pydantic import Field, field_validator
from typing import Any, Dict, Optional, List, Tuple

from ..interfaces.query_interface import QueryInterface
from ...types_var import Fields


class SqlQuery(QueryInterface):
    filters: Optional[Dict[Fields, Any]] = None
    limit: Optional[int] = Field(
        None, ge=1, description="Maximum number of records to return"
    )
    offset: Optional[int] = Field(None, ge=0, description="Number of records to skip")
    order_by: Optional[List[Tuple[Fields, str]]] = Field(
        None, description="List of (field, direction) tuples for sorting"
    )

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError(f"Limit must be greater than 0, got {v}")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError(f"Offset must be greater than or equal to 0, got {v}")
        return v

    @field_validator("order_by")
    @classmethod
    def validate_order_by(
        cls, v: Optional[List[Tuple[Fields, str]]]
    ) -> Optional[List[Tuple[Fields, str]]]:
        if v:
            allowed_directions = {"asc", "desc"}
            for idx, (field, direction) in enumerate(v):
                if direction.lower() not in allowed_directions:
                    raise ValueError(
                        f"Direction must be 'asc' or 'desc' (case-insensitive), "
                        f"got '{direction}' at position {idx} for field '{field}'"
                    )
                v[idx] = (field, direction.lower())
        return v

    @field_validator("filters")
    @classmethod
    def validate_filters(
        cls, v: Optional[Dict[Fields, Any]]
    ) -> Optional[Dict[Fields, Any]]:
        if v is not None and not isinstance(v, dict):
            raise ValueError(f"Filters must be a dictionary, got {type(v).__name__}")
        return v

    def add_filter(self, field: Fields, value: Any) -> "Query[Fields]":
        if self.filters is None:
            self.filters = {}
        self.filters[field] = value
        return self

    def remove_filter(self, field: Fields) -> "Query[Fields]":
        if self.filters and field in self.filters:
            del self.filters[field]
        return self

    def add_order_by(self, field: Fields, direction: str = "asc") -> "Query[Fields]":
        if self.order_by is None:
            self.order_by = []
        direction_lower = direction.lower()
        if direction_lower not in {"asc", "desc"}:
            raise ValueError(f"Direction must be 'asc' or 'desc', got '{direction}'")
        self.order_by.append((field, direction_lower))
        return self

    def clear_order_by(self) -> "Query[Fields]":
        self.order_by = None
        return self

    def clear_filters(self) -> "Query[Fields]":
        self.filters = None
        return self

    def reset(self) -> "Query[Fields]":
        self.filters = None
        self.limit = None
        self.offset = None
        self.order_by = None
        return self
