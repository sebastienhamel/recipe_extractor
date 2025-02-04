#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Start MySQL in the background
echo "Starting MySQL..."
service mysql start

# Start redis server
echo "Starting Redis..."
service redis-server start

export PATH="/app/venv/bin:$PATH"

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until mysqladmin ping -h localhost --silent; do
    sleep 2
done
echo "MySQL is ready!"

# Create a temporary SQL file with actual credentials
envsubst < /docker-entrypoint-initdb.d/mysql-init.sql > /tmp/mysql-init.sql

# Run the SQL script
echo "Initializing database credentials from file"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < /tmp/mysql-init.sql

# Activate virtual environment
echo "Activating virtual environment"
source /app/venv/bin/activate

# Apply Alembic migrations
echo "Running Alembic migrations..."
alembic stamp head
alembic upgrade head

# Starting celery
echo "Starting Celery worker"
export PYTHONPATH=$/app/src:$PYTHONPATH
celery -A tasks worker --loglevel=info

# Start the application (modify this line for your app)
echo "Starting the application..."
/bin/bash  # Modify this line if needed
