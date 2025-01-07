# pull python base image
FROM python:3.12-slim

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip/*

COPY . .

EXPOSE 8001

CMD ["python", "app.py"]