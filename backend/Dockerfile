FROM python:3.11-slim

WORKDIR /app

# System deps needed for psycopg2, pdfplumber, prophet, xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/resumes uploads/datasets uploads/reports artifacts chroma_store

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
