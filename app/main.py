#from fastapi import FastAPI
#from app.api import endpoints
#import os

#app = FastAPI(title="OCR Scanner API")
#app.include_router(endpoints.router)


from fastapi import FastAPI
from app.api import endpoints
import os
import uvicorn

app = FastAPI(title="OCR Scanner API")
app.include_router(endpoints.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

 
