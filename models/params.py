from pydantic import BaseModel, Field
from typing import Optional

class ParamsModel(BaseModel):
    """
    Request parameters for the API endpoint.
    Each optional field can contain metadata for dynamic SQL query building.
    """
    start_time: str = Field(..., description="Start time (required)")
    
    end_time: Optional[str] = Field(
        None, 
        description="End time (optional)",
        json_schema_extra={
            "query_part": "AND creation_date <= @end_time",
            "bq_type": "STRING"
        }
    )
    
    limit: Optional[int] = Field(
        None, 
        description="Limit (optional)",
        json_schema_extra={
            "query_part": "LIMIT @limit",
            "bq_type": "INT64"
        }
    )
    
    offset: Optional[int] = Field(
        None, 
        description="Offset (optional)",
        json_schema_extra={
            "query_part": "OFFSET @offset",
            "bq_type": "INT64"
        }
    )
    
    staff_id: Optional[int] = Field(
        None,
        description="Staff ID (optional)",
        json_schema_extra={
            "query_part": "AND owner_user_id = @staff_id",
            "bq_type": "INT64"
        }
    ) 