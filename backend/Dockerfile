FROM python:3.12-slim

WORKDIR /app

# Build deps for psycopg and sentence-transformers' native wheels
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
