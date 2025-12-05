from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class BuildFilters(BaseModel):
    category: Optional[str] = None
    month: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

pyOutPutParser = PydanticOutputParser(pydantic_object=BuildFilters)

class FirestoreTransactionQuery(BaseModel):
    """
    Query schema with optional filters:
    - date (ms timestamp or operator dict)
    - category
    - amount
    
    month: separate field in "YYYY-MMM" (e.g., 2025-Apr)
    isAllData: automatically true if month is not provided
    """

    month: Optional[str] = Field(
        description="Month in 'MMM' format, e.g., 'Apr'."
    )

    filters: Optional[Dict[str, Any]] = Field(
        description=(
            "Optional filters. Allowed keys: date, category, amount.\n"
            "Each may be a value or an operator dict."
        )
    )

    isAllData: Optional[bool] = Field(
        default=None,
        description="If month is not provided, this becomes True automatically."
    )

    @field_validator("month")
    def validate_month(cls, value):
        if value is None:
            return value
        year = datetime.now().year
        return f"{year}-{value}"

    @field_validator("filters")
    def validate_filters(cls, filters):
        if filters is None:
            return filters

        allowed = {"date", "category", "amount"}

        for key, value in filters.items():
            if key not in allowed:
                raise ValueError(f"Invalid filter key '{key}'. Allowed: {allowed}")

            if key == "date":
                if isinstance(value, int):
                    continue
                if isinstance(value, dict):
                    for v in value.values():
                        if not isinstance(v, int):
                            raise ValueError("date operator values must be integer timestamps")
                else:
                    raise ValueError("date must be int or operator dict")

        return filters




pyOutPutParser2 = PydanticOutputParser(pydantic_object=FirestoreTransactionQuery)
