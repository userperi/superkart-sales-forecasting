# Use a minimal base image with Python 3.12 installed
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install the dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code and the serialized model
COPY . .

# The Flask API listens on port 7860
EXPOSE 7860

# Start the Flask app with gunicorn: 4 workers, bound to port 7860 on all interfaces
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
