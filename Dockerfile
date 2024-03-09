# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Flask app code into the container
COPY . .

# Install required Python packages
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the Flask app with gunicorn when the container starts
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

# Start the RQ worker
CMD ["rq", "worker", "--url", "redis://192.168.1.95:6379/0"]