import logging
import os
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError
from typing import List, Dict, Any
from models.params import ParamsModel

logger = logging.getLogger(__name__)

# --- BigQuery Configuration ---
# Load configuration from environment variables.
# For production, you should set these variables in your deployment environment.
# Your GCP project ID for billing and authentication purposes.
PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")
# The fully qualified ID of the table to query.
TABLE_ID = os.getenv("BIGQUERY_TABLE_ID", "bigquery-public-data.stackoverflow.posts_questions")

if not PROJECT_ID:
    logger.warning(
        "BIGQUERY_PROJECT_ID environment variable is not set. The client will use the "
        "default project from your gcloud setup. It is recommended to set this "
        "explicitly for production environments for billing and authentication."
    )


class BigQueryService:
    """
    A service class for handling BigQuery operations.
    """
    def __init__(self):
        """
        Initializes the BigQueryService, explicitly setting the project for the client.
        """
        self.client = bigquery.AsyncClient(project=PROJECT_ID)

    async def query_data(self, params: ParamsModel) -> List[Dict[str, Any]]:
        """
        Queries BigQuery based on the provided parameters using an async client.
        """
        logger.info("BigQuery query params: %s", params)
        
        sql_parts = [
            f"SELECT question_id, title, tags, creation_date, owner_user_id",
            f"FROM `{TABLE_ID}`",
            "WHERE creation_date >= @start_time"
        ]
        
        query_params = [
            bigquery.ScalarQueryParameter("start_time", "STRING", params.start_time)
        ]

        # Dynamically build query from model metadata
        for field_name, field_info in params.model_fields.items():
            metadata = field_info.json_schema_extra or {}
            query_part = metadata.get("query_part")
            
            if query_part:
                value = getattr(params, field_name, None)
                if value is not None:
                    sql_parts.append(query_part)
                    bq_type = metadata.get("bq_type", "STRING") # Default to STRING if not specified
                    query_params.append(bigquery.ScalarQueryParameter(field_name, bq_type, value))
        
        # Manually add ORDER BY to ensure it's placed correctly before LIMIT/OFFSET.
        # A more sophisticated system might use an 'order' key in the metadata.
        sql_parts.append("ORDER BY creation_date DESC")

        sql = ' '.join(sql_parts)
        logger.info("BigQuery SQL: %s", sql)
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        try:
            query_job = await self.client.query(sql, job_config=job_config)
            results = [dict(row) async for row in query_job]
            logger.info("BigQuery query success, %d rows.", len(results))
            return results
        except GoogleAPICallError as e:
            logger.error("BigQuery error: %s", e, exc_info=True)
            raise Exception("Failed to retrieve data from BigQuery.") from e

# Create a single, reusable instance of the service
bigquery_service = BigQueryService()

def get_bigquery_service() -> BigQueryService:
    """
    Dependency function to get the singleton BigQueryService instance.
    """
    return bigquery_service 