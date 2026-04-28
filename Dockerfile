FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY agent/ agent/
COPY frontend/ frontend/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "agent.main"]
