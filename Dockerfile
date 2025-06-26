FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY astro_engine/requirementsDev.txt .
RUN pip install --no-cache-dir -r requirementsDev.txt

# Copy the application code
COPY astro_engine /app/astro_engine

# Set the ephemeris path environment variable
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "-m", "astro_engine.app", "--production"]
