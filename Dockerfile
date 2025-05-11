# Step 1: Base Image Choose Karna (Python Image)
FROM python:3.11

# Step 2: Working Directory Set Karna
WORKDIR /app

# Step 3: Local Python files ko Docker container mein copy karna
COPY ./backend /app/backend
COPY ./frontend /app/frontend

# Step 4: Python Dependencies Install Karna
COPY backend/requirements.txt /app/requirements.txt
RUN pip install  -r /app/requirements.txt

# Step 5: Expose Backend Port (API runs on this port)
EXPOSE 8000

# Step 6: Backend app ko run karna
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
