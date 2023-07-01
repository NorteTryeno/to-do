from fastapi.testclient import TestClient
from sqlalchemy import select


from src.database import get_async_session
from src.main import app
from src.posts.models import Task

client = TestClient(app)


async def override_get_async_session():
    async with get_async_session() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


def test_get_task():

    task1 = Task(title="Task 1", description="Description 1")
    task2 = Task(title="Task 2", description="Description 2")

    with TestClient(app) as client:
        with get_async_session() as session:
            session.add_all([task1, task2])
            session.commit()

            response = client.get("/get_task", params={"task_title": "Task 1"})
            assert response.status_code == 200

            data = response.json()
            assert len(data) == 1

            task = data[0]
            assert task["title"] == "Task 1"
            assert task["description"] == "Description 1"


def test_get_all():
    limit1, offset1 = 1, 0
    limit2, offset2 = 2, 1

    task1 = Task(title="Task 1", description="Description 1")
    task2 = Task(title="Task 2", description="Description 2")
    task3 = Task(title="Task 3", description="Description 3")

    with TestClient(app) as client:
        with get_async_session() as session:
            session.add_all([task1, task2, task3])
            session.commit()

            response1 = client.get("/get_all", params={"limit": limit1, "offset": offset1})
            assert response1.status_code == 200

            data1 = response1.json()
            assert len(data1) == limit1

            task1 = data1[0]
            assert task1["title"] == "Task 1"
            assert task1["description"] == "Description 1"

            response2 = client.get("/get_all", params={"limit": limit2, "offset": offset2})
            assert response2.status_code == 200

            data2 = response2.json()
            assert len(data2) == limit2

            task2 = data2[0]
            task3 = data2[1]

            assert task2["title"] == "Task 2"
            assert task2["description"] == "Description 2"
            assert task3["title"] == "Task 3"
            assert task3["description"] == "Description 3"


def test_add_task():
    task1 = {"title": "Task 1", "description": "Description 1", "completed": False}

    with TestClient(app) as client:
        with get_async_session() as session:
            response = client.post("/add_task", json=task1)
            assert response.status_code == 200
            assert response.json() == {"200": "nicely done"}

            result = await session.execute(select(Task).where(Task.title == task1["title"]))
            task = result.scalar_one_or_none()
            assert task is not None
            assert task.title == task1["title"]
            assert task.description == task1["description"]
            assert task.completed == task1["completed"]


def test_update_task():
    new_t = "Test_Update"
    new_d = "Test_Description_Updated"
    o_d = "Task 1"
    with TestClient(app) as client:
        with get_async_session() as session:
            response1 = client.post("/update_task", params={"new_task_title": new_t, "new_task_desc": new_d, "old_task": o_d})
            assert response1.status_code == 200
            assert response1.json() == {"message": "Task updated successfully"}

            result = await session.execute(select(Task).where(Task.title == new_t))
            task = result.scalar_one_or_none()
            assert task is not None
            assert task.title == new_t
            assert task.title != o_d
            assert task.description == new_d


def test_mark_complete():

    marked_test_title = "Test_Update"
    togle = True

    with TestClient(app) as client:
        with get_async_session() as session:

            response = client.post("/mark_complete", params={"marked_title": marked_test_title, "togle": togle})
            assert response.status_code == 200
            assert response.json() == {f'{marked_test_title}': 'changed'}

            result = await session.execute(select(Task).where(Task.title == marked_test_title))
            task = result.scalar_one_or_none()
            assert task is not None
            assert task["completed"] == togle


def test_delete_task():

    task_title = "Test Task"

    with TestClient(app) as client:
        with get_async_session() as session:

            task = Task(title=task_title)
            session.add(task)
            session.commit()

            response = client.delete("/del_task", params={"task_title": task_title})
            assert response.status_code == 200
            assert response.json() == {"200": "success"}

            result = await session.execute(select(Task).where(Task.title == task_title))
            task_completion = result.scalar_one_or_none()
            assert task_completion is None
