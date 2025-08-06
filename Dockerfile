# Use the official Python 3.8 slim image as the base image
FROM python:3.9-slim

ARG ABEXP_SCORE_COLUMN
ARG SECRET_KEY
ARG FLASK_ENV

ENV FLASK_ENV=${FLASK_ENV}
ENV DATA_PATH='/data'
ENV ABEXP_SCORE_COLUMN=${ABEXP_SCORE_COLUMN}
ENV SECRET_KEY=${SECRET_KEY}

# Set the working directory within the container
WORKDIR /app

# install dependencies
COPY poetry.lock pyproject.toml .flaskenv README.md /app/
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-root

# copy source code
COPY abexp_web/ ./abexp_web/
RUN poetry install --only-root

# Expose port 5000 for the Flask application
EXPOSE 5000