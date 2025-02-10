FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /logs

EXPOSE 8000

CMD ["python", "app/main.py"]