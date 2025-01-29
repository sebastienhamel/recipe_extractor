#!/bin/bash

# Start MySQL service
service mysql start
sleep 5  # Give MySQL time to start

# Create a temporary SQL file with actual credentials
envsubst < /docker-entrypoint-initdb.d/mysql-init.sql > /tmp/mysql-init.sql

# Run the SQL script
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < /tmp/mysql-init.sql

# activate the venv
. /app/venv/bin/activate

# Run Alembic migrations
# python3 -m alembic upgrade head

echo "Python executable: $(which python3)"
echo "Alembic executable: $(which alembic)"

python3
