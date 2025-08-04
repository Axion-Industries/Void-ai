# Stage 1: Build the Frontend
# This stage uses a Node.js image to build the static frontend assets.
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Copy frontend-specific files
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ ./
# Set Supabase env vars during build time to be embedded in the static files
# These are safe to be public as they are the public anon keys.
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}
RUN npm run build


# Stage 2: Build the Python Backend
# This stage builds the final Python application and copies the built frontend assets.
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Copy the built frontend assets from the first stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create required directories and set permissions
RUN mkdir -p logs out data/void && chmod -R 755 logs out data/void

# Run model setup and verification at build time
RUN python3 setup_model.py || exit 1
RUN python3 verify_setup.py || exit 1

# Set environment variables for the application
ENV MODEL_PATH=/app/out/model.pt \
    VOCAB_PATH=/app/data/void/vocab.pkl \
    META_PATH=/app/data/void/meta.pkl \
    PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 10000

# Run the application using Gunicorn
CMD exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 chat_api:app
