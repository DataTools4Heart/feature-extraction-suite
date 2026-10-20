#!/bin/bash

# stop containers first, so nothing holds or re-creates the bind-mounted directories
docker compose -f feature-extraction-suite/docker/repofyr/docker-compose-repofyr.yml --project-directory ./ -p dt4h-repofyr-feast down -v
# remove output-data directory
rm -rf feature-extraction-suite/output-data/
# remove postgres data
rm -rf feature-extraction-suite/postgres-data/