FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install basic dependencies
RUN pip install --no-cache-dir openai python-dotenv whisper python-pptx

# Create directories
RUN mkdir -p /app/data /app/logs /app/traces

# Copy source code when it's ready
# COPY src/ /app/src/
# COPY scripts/ /app/scripts/

# Default command
CMD ["echo", "Voice Concierge container is ready. Mount volumes and provide commands to run."]
