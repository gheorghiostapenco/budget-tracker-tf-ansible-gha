# Stage 1: Use a minimal Python image as the base
# We use a slim version to keep the image size small
FROM python:3.11-slim

# Set environment variables for non-buffered output and server port
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 5000

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the working directory
# This step is cached separately
COPY requirements.txt .

# Install the Python dependencies (including Gunicorn)
# --no-cache-dir: prevents pip from storing cache, reducing image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the application is configured to listen on
EXPOSE 5000

# Command to run the application using the Gunicorn WSGI server
# -w 4: 4 worker processes (a good starting point for a 1-4 core machine)
# -b 0.0.0.0:5000: Binds Gunicorn to all interfaces on port 5000
# app:app: Specifies the Flask application instance (variable 'app' in file 'app.py')
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
