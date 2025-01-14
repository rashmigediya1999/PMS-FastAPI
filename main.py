import pandas as pd

from fastapi import FastAPI
from app.core.config import settings
from app.db.mongodb import MongoDB
from app.api.routes import payments
from app.utils.csv_load_service import load_and_normalize_csv_data
from app.core import Logger
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.config["app"]["title"],
        description=settings.config["app"]["description"],
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.config["server"]["origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    


    # Setup logging
    Logger.setup_logging()

    # Register startup and shutdown events
    app.add_event_handler("startup", MongoDB.connect)
    app.add_event_handler("startup", load_csv_data)
    app.add_event_handler("shutdown", MongoDB.close)

    # Register routes
    app.include_router(payments.router, prefix="/api/v1", tags=["payments"])
    # app.include_router(files.router, prefix="/api/v1", tags=["files"])
    
    return app


async def load_csv_data():
    try:
        file_path = settings.config["data"]["file_path"]
        collection_name = settings.config["mongodb"]["collections"]["payments"]

        logger.info(f"Loading data from '{file_path}'")    
        await load_and_normalize_csv_data(file_path, collection_name)
    except Exception as e:
        logger.error(f"Failed to load data from '{file_path}': {e}")

app = create_app()
logger = Logger.get_logger(__name__)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.config["server"]["host"],
        port=settings.config["server"]["port"],
        reload=settings.config["server"]["reload"],
        workers=settings.config["server"]["workers"]
    )