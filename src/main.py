from fastapi import FastAPI

from src.posts.router import router as router_task
app = FastAPI()


@app.get('/')
def init():
    return {"200": "Hello, World!"}


app.include_router(router_task)