#from fastapi import FastAPI
#from app.api import endpoints
#import os

#app = FastAPI(title="OCR Scanner API")
#app.include_router(endpoints.router)


from fastapi import FastAPI
from app.api import endpoints
import os
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

app = FastAPI(title="OCR Scanner API")
app.include_router(endpoints.router)

if __name__ == "__main__":
    config = Config()
    config.bind = [f"[::]:{os.environ.get('PORT', 8000)}"]
    asyncio.run(serve(app, config))

 
