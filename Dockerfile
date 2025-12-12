# Dockerfile for CrewCFO Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
# 8000 = FastAPI backend
# 8501 = Streamlit dashboard
EXPOSE 8000 8501

# Default command (FastAPI)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
