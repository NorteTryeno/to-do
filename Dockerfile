FROM python:3.9

WORKDIR /to-do/src/main:app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD uvicorn src.main:app --reload
