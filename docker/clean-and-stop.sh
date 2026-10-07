#!/bin/bash

# stop containers first, so nothing holds or re-creates the bind-mounted directories
docker compose -f feature-extraction-suite/docker/docker-compose.yml --project-directory ./ -p dt4h-onfhir-feast down -v
# remove output-data directory
rm -rf feature-extraction-suite/output-data/
# remove postgres data
rm -rf feature-extraction-suite/postgres-data/