from fastapi import FastAPI
from app.api import endpoints
import os
import uvicorn

app = FastAPI(title="OCR Scanner API")
app.include_router(endpoints.router)

# Add this:
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)