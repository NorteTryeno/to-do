from pydantic import BaseModel


class TaskCreate(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
