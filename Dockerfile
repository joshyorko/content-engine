FROM python:3.11-slim


# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy the requirements file to the working directory
COPY ./src .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY src/ /app/

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose port 8003 to the outside world
EXPOSE 8000


# Add a script to run the migrations and start the server
COPY entrypoint.sh /app/
COPY wait-for-it.sh /app/

RUN chmod +x /app/wait-for-it.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]