FROM python:3.11
WORKDIR /app
COPY . /app/backend /app/frontend /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

