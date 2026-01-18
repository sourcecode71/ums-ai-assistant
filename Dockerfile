# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file if exists
COPY requirements.txt .

# Install dependencies SYSTEM-WIDE (not --user)
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app

# Switch to non-root user
USER app

# Verify uvicorn is accessible
RUN which uvicorn && uvicorn --version

# Copy application code (as non-root user)
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Use full path to uvicorn
CMD ["/usr/local/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]