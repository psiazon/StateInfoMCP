
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV PYTHONUNBUFFERED=1
ENV MCP_HOST=0.0.0.0
ENV PORT=8001

EXPOSE 8001

CMD ["python", "-m", "app.main"]
