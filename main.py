from fastapi import FastAPI

from middlewares import CustomHeaderMiddleware
from src.routes import contacts

app = FastAPI()

app.include_router(contacts.router, prefix='/api')
app.add_middleware(CustomHeaderMiddleware)


@app.get("/")
def read_root():
    return {"Message": "Welcome to FastAPI!"}
