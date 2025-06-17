# Dockerfile (root of your repo)
FROM python:3.11

WORKDIR /app

# 1) Copy only requirements, install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Now copy the rest of your application
COPY . .

# Make sure frontend directory exists and create if needed
RUN mkdir -p /app/frontend

# Copy frontend files specifically (in case they weren't copied in the COPY . . step)
COPY ./frontend/*.html /app/frontend/

# Verify the contents
RUN echo "Contents of the workspace:" && ls -la && \
    echo "Contents of frontend directory:" && ls -la /app/frontend

# 3) Start Uvicorn with debugging information
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
