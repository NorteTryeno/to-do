from sqlalchemy import Table, Column, Integer, String, Boolean

from src.database import metadata

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("description", String, nullable=True),
    Column("completed", Boolean),
)