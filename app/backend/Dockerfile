FROM python:3.11-slim

WORKDIR /app

# Install dependency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code backend
COPY main.py .

# Expose port internal container
EXPOSE 8000

# Jalankan server
CMD ["python3", "main.py"]
