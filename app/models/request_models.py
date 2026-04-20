from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question about the uploaded document")
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
        description="Optional retrieval depth override for this query",
    )
