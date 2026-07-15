"""
Data models for the QueryOpt API using Pydantic.
Ensures strict type checking and validation for all incoming requests and outgoing responses.
"""

from pydantic import BaseModel
from typing import List, Optional

class BasicAnalysisRequest(BaseModel):
    query: str
    schema_text: str

class DeepAnalysisRequest(BaseModel):
    query: str

class IndexSuggestion(BaseModel):
    index_name: str
    create_statement: str
    reason: str

class AnalysisResponse(BaseModel):
    is_slow: bool
    issue: str
    issue_type: str
    optimized_query: str
    suggested_indexes: List[IndexSuggestion]
    explanation: str
    execution_plan: Optional[str] = None
