#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Start MySQL in the background
echo "Starting MySQL..."
service mysql start

export PATH="/app/venv/bin:$PATH"

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until mysqladmin ping -h localhost --silent; do
    sleep 2
done
echo "MySQL is ready!"

# Run MySQL initialization script (if applicable)
if [ -f "/docker-entrypoint-initdb.d/mysql-init.sql" ]; then
    echo "Initializing database..."
    mysql < /docker-entrypoint-initdb.d/mysql-init.sql
fi

# Activate virtual environment
echo "Activating virtual environment"
source /app/venv/bin/activate

# # Apply Alembic migrations
# echo "Running Alembic migrations..."
# alembic upgrade head

# Start the application (modify this line for your app)
echo "Starting the application..."
/bin/bash  # Modify this line if needed
