"""
Main entry point for App Engine deployment.
This serves the FastAPI backend API.
"""
from backend.api.main import app

# The app is already defined in backend.api.main
# App Engine will use this as the entry point
