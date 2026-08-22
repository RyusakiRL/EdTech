"""Main entry point for the FastAPI application."""

from pathlib import Path
from fastapi import FastAPI
from routers import inventory_router, users_router, auth_router, cards_router

app = FastAPI(
    title="Logistics API - B2B Industrial Engine",
    description="API for managing logistics operations",
    version="1.0.0",
)
UPLOADS_FOLDER = Path("uploads")
UPLOADS_FOLDER.mkdir(exist_ok=True)
app.include_router(inventory_router.router)
app.include_router(users_router.router)
app.include_router(auth_router.router)
app.include_router(cards_router.router)


@app.get("/")
def root():
    """Test endpoint to check if the API is running."""
    return {"message": "Motor V12 Online. System ready for operations."}
