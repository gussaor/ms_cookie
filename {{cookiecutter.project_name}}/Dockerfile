FROM python:3.10-slim-buster as requirements-stage
WORKDIR /tmp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN apt-get clean && apt-get -y update && apt-get install -y locales && locale-gen es_ES.UTF-8
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10-slim-buster as develoment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /home/{{cookiecutter.project_slug}}
COPY ./pyproject.toml ./poetry.lock* ./
RUN pip install poetry
RUN poetry install
RUN apt-get clean && apt-get -y update && apt-get install -y locales && locale-gen es_ES.UTF-8
CMD ["poetry","run" , "uvicorn", "main:app", "--host", "0.0.0.0"]

FROM python:3.10-slim-buster as production
RUN mkdir -p /home/{{cookiecutter.project_slug}}
RUN addgroup --system app && adduser --system --group app
ENV APP_home=/home/{{cookiecutter.project_slug}}
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT=local

WORKDIR $APP_home
COPY --from=requirements-stage /tmp/requirements.txt /home/{{cookiecutter.project_slug}}/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /home/{{cookiecutter.project_slug}}/requirements.txt
COPY . $APP_home
RUN chown -R app:app $APP_home
USER app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]