from typing import Generic, TypeVar, List
from pydantic import BaseModel, create_model

from app.api.schemas.quickbooks_schema import TransactionModel

# Define a generic type for the data content
DataT = TypeVar('DataT')

class PageResponse(BaseModel, Generic[DataT]):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int
    content: List[DataT]

# Example usage with a specific type (e.g., TransactionModel)
# You can create a specific PageResponse model for different data types as needed.
TransactionPageResponse = create_model(
    'TransactionPageResponse', 
    __base__=PageResponse[TransactionModel]  # Assuming TransactionModel is your data model
)
