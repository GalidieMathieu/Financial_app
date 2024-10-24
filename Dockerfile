FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Django's port
EXPOSE 8000

# Use the correct command to start Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
