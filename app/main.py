from fastapi import FastAPI
from app.api import endpoints
import os

app = FastAPI(title="OCR Scanner API")
app.include_router(endpoints.router)

 
