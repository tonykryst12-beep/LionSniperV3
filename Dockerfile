# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (needed by Render)
EXPOSE 10000

# Start command to keep container alive
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]
