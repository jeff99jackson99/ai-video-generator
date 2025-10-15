"""Entry point for running the application."""

import uvicorn
from src.core.config import Config

if __name__ == "__main__":
    uvicorn.run(
        "src.app.web:app",
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=Config.DEBUG
    )
