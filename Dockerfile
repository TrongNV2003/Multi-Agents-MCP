# Tầng 1: "builder" để cài đặt dependencies
FROM python:3.11 as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-dev --no-root

# Tầng 2: Image cuối cùng, gọn nhẹ
FROM python:3.11-slim

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

COPY --from=builder /usr/local/ /usr/local/

COPY . .

EXPOSE 2206

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "2206"]