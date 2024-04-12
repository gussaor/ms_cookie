FROM {{cookiecutter.docker_image}} as requirements-stage
WORKDIR /tmp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN apt-get clean && apt-get -y update && apt-get install -y locales && locale-gen es_ES.UTF-8
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM {{cookiecutter.docker_image}} as develoment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /home/pdf_creator
COPY ./pyproject.toml ./poetry.lock* ./
RUN pip install poetry
RUN poetry install
RUN apt-get clean && apt-get -y update && apt-get install -y locales && locale-gen es_ES.UTF-8
CMD ["poetry","run" , "uvicorn", "main:app", "--host", "0.0.0.0"]

FROM {{cookiecutter.docker_image}} as production
RUN mkdir -p /home/{{cookiecutter.project_slug}}
RUN addgroup --system app && adduser --system --group app
ENV APP_home=/home/pdf_creator
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT=local
WORKDIR $APP_home
COPY --from=requirements-stage /tmp/requirements.txt /home/pdf_creator/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /home/pdf_creator/requirements.txt
COPY . $APP_home
RUN chown -R app:app $APP_home
USER app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]