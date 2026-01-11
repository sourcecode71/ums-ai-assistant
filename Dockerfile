# Use multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Copy requirements FIRST for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Install system dependencies ChromaDB needs
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Copy application code (after user creation for better security)
COPY --chown=app:app . .

EXPOSE 8000

# Use uvicorn for production (better than python main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]