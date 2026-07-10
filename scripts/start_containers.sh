#!/bin/bash
echo "Deploying Docker Containers..."
docker compose -f containers/docker-compose.yml up -d
echo "Containers are now running! Use 'docker ps' to verify."
