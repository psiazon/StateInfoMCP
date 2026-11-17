FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PORT=8001
EXPOSE 8001
RUN useradd --create-home --uid 10001 appuser
USER appuser
CMD ["python", "-m", "app.main"]
