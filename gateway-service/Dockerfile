FROM python:3.9-slim

WORKDIR /app/

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Start the service
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080