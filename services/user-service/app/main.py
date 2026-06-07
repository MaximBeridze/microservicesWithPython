# Entry point — FastAPI application.
#
# This file creates the FastAPI app instance and registers the router.
# Keep it minimal: no business logic, no endpoints defined here.
#
# To run the service locally:
#   uvicorn app.main:app --reload --port 8001
#
# Then open: http://localhost:8001/docs
#
# See the README for the full implementation.

from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="user-service")
app.include_router(router)