import logging
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from routers.params_router import router as params_router

# Load environment variables from .env file before anything else
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI()

app.include_router(
    params_router,
    prefix="/params",
    tags=["Params"]
)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True) 