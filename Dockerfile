
# Use Python image
FROM python:3.10-slim

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install required python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Start bot
CMD ["python", "main.py"]
