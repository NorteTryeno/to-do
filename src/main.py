from fastapi import FastAPI

from src.posts.router import router as router_task
app = FastAPI()

app.include_router(router_task)
