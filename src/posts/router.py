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


async def get_by_title(title: str, session):
    stmt = await session.execute(select(Task).where(Task.title == title))

    task = stmt.scalar()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


async def selection(task_op, column_name, session):
    column = getattr(Task, column_name, None)

    if not column:
        raise HTTPException(status_code=400, detail="Incorrect column name")

    try:
        task_op = int(task_op)
        filter_expr = column == task_op
    except ValueError:
        if column_name == 'completed':
            if task_op.lower() == 'false':
                filter_expr = column == False
            elif task_op.lower() == 'true':
                filter_expr = column == True
            else:
                raise HTTPException(status_code=400, detail="Invalid value for task_op")
        else:
            raise HTTPException(status_code=400, detail="Invalid value for task_op")

    query = await session.execute(select(Task).where(filter_expr))

    return query


@router.get('/get_task')
async def get_task(task_title, column: str = 'title', session: AsyncSession = Depends(get_async_session)):
    query = await selection(task_op=task_title, column_name=column, session=session)

    rows = query.fetchall()
    columns = query.keys()

    final = [dict(zip(columns, row)) for row in rows]

    return final


@router.get('/get_all')
async def get_all(limit: int = 1, offset: int = 1, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Task))

    rows = result.fetchall()
    columns = result.keys()

    final = [dict(zip(columns, row)) for row in rows]

    return final[offset:][:limit]


@router.post('/add_task')
async def add_task(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Task).values(**new_task.dict())

    await session.execute(stmt)
    await session.commit()

    return {"200": "nicely done"}


@router.post('/update_task')
async def update_task(new_task_title: str, new_task_desc: str, old_task: str,
                      session: AsyncSession = Depends(get_async_session)):
    task = await get_by_title(old_task, session)

    task.title = new_task_title
    task.description = new_task_desc

    await session.commit()

    return {"message": "Task updated successfully"}


@router.post('/mark_complete')
async def mark_complete(marked_title: str, togle: bool, session: AsyncSession = Depends(get_async_session)):
    task = await get_by_title(marked_title, session)

    task.completed = togle

    return {f'{marked_title}': 'changed'}


@router.delete('/del_task')
async def del_task(task_title: str, session: AsyncSession = Depends(get_async_session)):
    task = await get_by_title(task_title, session)

    await session.delete(task)
    await session.commit()

    return {"200": "success"}
