import logging
from fastapi import APIRouter, Depends, HTTPException
from models.params import ParamsModel
from fastapi import Query, Path
from typing import List, Dict, Any
from services.big_query_search import BigQueryService, get_bigquery_service

router = APIRouter()
logger = logging.getLogger(__name__)

def get_params(
    start_time: str = Path(..., description="Start time (required)"),
    end_time: str = Query(None, description="End time (optional)"),
    limit: int = Query(None, description="Limit (optional)"),
    offset: int = Query(None, description="Offset (optional)"),
    staff_id: int = Query(None, description="Staff ID (optional)")
) -> ParamsModel:
    return ParamsModel(
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
        staff_id=staff_id
    )

@router.get("/{start_time}")
async def get_with_params(
    params: ParamsModel = Depends(get_params),
    bq_service: BigQueryService = Depends(get_bigquery_service)
) -> List[Dict[str, Any]]:
    """
    Get API with required start_time path parameter and optional query parameters.
    This endpoint queries a BigQuery public dataset.
    """
    logger.info("Received request to query BigQuery with parameters: %s", params)
    try:
        results = await bq_service.query_data(params)
        logger.info("Successfully retrieved %d records.", len(results))
        return results
    except Exception as e:
        logger.error("An unexpected error occurred in the endpoint: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Our team has been notified."
        ) 