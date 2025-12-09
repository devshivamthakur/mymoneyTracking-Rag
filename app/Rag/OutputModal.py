from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class BuildFilters(BaseModel):
    category: Optional[str] = None
    month: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

pyOutPutParser = PydanticOutputParser(pydantic_object=BuildFilters)

class FirestoreTransactionQuery(BaseModel):
    month: Optional[str] = Field(
        description="Month in 'MMM' format, e.g., 'Apr'."
    )

    isAllData: Optional[bool] = Field(
        default=None,
        description="If month is not provided, this becomes True automatically."
    )
    
    isQueryToAppFinanceRelated: Optional[bool] = Field(
        default=False,
        description=(
            "Determines whether the user’s query is related to personal/app finances.\n\n"
            "Set to True WHEN the user's query involves financial information stored "
            "in Firestore, such as:\n"
            "- 'How much did I spend today?'\n"
            "- 'Show my expenses for April.'\n"
            "- 'What was my biggest purchase this week?'\n"
            "- 'List my transactions with category Food.'\n"
            "- 'How much did I earn last month?'\n\n"
            "Set to False WHEN the user's query is general conversation or unrelated "
            "to personal finance, such as:\n"
            "- 'Hi', 'Hello', 'How are you?'\n"
            "- 'Tell me a joke.'\n"
            "- 'Explain machine learning.'\n"
            "- Any question not requiring Firestore financial data.\n\n"
            "If True → Firestore search will be executed.\n"
            "If False → The query will be answered by another LLM without Firestore."
        )
    )

    @field_validator("month")
    def validate_month(cls, value):
        if value is None:
            return value
        year = datetime.now().year
        return f"{year}-{value}"

pyOutPutParser2 = PydanticOutputParser(pydantic_object=FirestoreTransactionQuery)
