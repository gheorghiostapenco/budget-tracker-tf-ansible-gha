# Dockerfile

# Stage 1: Use a minimal Python image as the base
# We use a slim version to keep the image size small
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir: prevents pip from storing cache, reducing image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes app.py and the templates directory
COPY . .

# Expose the port that Flask is configured to listen on (5000)
# This is documentation and does not actually publish the port
EXPOSE 5000

# Command to run the application when the container starts
# We use the Gunicorn WSGI server for a more robust production setup
# For simplicity with Flask's built-in server:
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
# Alternatively, for production readiness, install Gunicorn in requirements.txt and use: 
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]