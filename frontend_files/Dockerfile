# Use a minimal base image with Python 3.12 installed
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the Streamlit app
COPY . .

# Streamlit runs on port 8501
EXPOSE 8501

# XSRF protection is disabled so file uploads work through the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
