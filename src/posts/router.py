from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.posts.models import Task
from src.posts.schema import TaskCreate

router = APIRouter(
    prefix='/tasks',
    tags=['task'],
)


@router.get('/get_task')
async def get_task(task_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Task).where(Task.title == task_title)
    result = await session.execute(query)
    rows = result.fetchall()
    columns = result.keys()
    final = [dict(zip(columns, row)) for row in rows]
    return final


@router.post('/add_task')
async def add_task(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Task).values(**new_task.dict())
    await session.execute(stmt)
    await session.commit()
    return {"200": "nicely done"}


@router.delete('/del_task')
async def del_task(task_title: str, session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(Task).filter(Task.title == task_title))
    task = stmt.scalar()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()

    return {"200": "success"}
