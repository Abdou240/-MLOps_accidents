#!/bin/bash

# Start PostgreSQL service
service postgresql start

# Wait for PostgreSQL to become available
echo "Waiting for PostgreSQL to start..."
sleep 10

uvicorn app:app --host 0.0.0.0 --port 9090


# Keep the container running
tail -f /dev/null