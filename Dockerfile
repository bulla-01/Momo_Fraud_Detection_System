# ---- Stage 1: Build stage ----
FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# ---- Stage 2: Runtime stage ----
FROM python:3.10-slim

# Create non-root user
RUN useradd -m appuser
WORKDIR /home/appuser

# Install netcat in runtime image too (for DB wait)
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Copy from build stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /home/appuser

# Copy start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set permissions
RUN chown -R appuser:appuser /home/appuser /start.sh

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Run startup script
CMD ["/start.sh"]
