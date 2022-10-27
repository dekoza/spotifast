FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install fastapi uvicorn poetry wheel virtualenv

EXPOSE 8000

WORKDIR /usr/src/spotifast

ENV PORT 8000
ENV HOST "0.0.0.0"
COPY ./src/ /spotifast
COPY ./pyproject.toml /spotifast
COPY ./poetry.lock /spotifast

WORKDIR /spotifast
RUN poetry config virtualenvs.create false && poetry install

CMD ["hypercorn", "spotifast.main:app", "--reload", "--bind", "0.0.0.0:8000"]
