# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code into the container
COPY . .

# Expose the service port
EXPOSE 5002

# Command to run the service
CMD ["python", "app.py"]