#!/bin/bash
# Set environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
ENV POSTGRES_PASSWORD="n-]23kLr92Zz"
ENV POSTGRES_DB="accidents_db"
ENV POSTGRES_USER="root"
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432

# Automatically start postgresql service when the container starts
echo "service postgresql start" >> ~/.bashrc

# Create a PostgreSQL role named `yourUsername` with 'yourPassword' as the password and
# then create a database `yourDatabaseName` owned by the `yourUsername` role.
RUN service postgresql start && \
    su - postgres -c "psql -c \"CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';\"" && \
    su - postgres -c "createdb -O $POSTGRES_USER $POSTGRES_DB" && \
    service postgresql stop

# Start PostgreSQL service
service postgresql start

# Wait for PostgreSQL to become available
echo "Waiting for PostgreSQL to start..."
sleep 10

# Execute the command specified as CMD in Dockerfile
#exec "$@"
python3 app.py

# Keep the container running
tail -f /dev/null