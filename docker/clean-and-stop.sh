#!/bin/bash

# remove output-data directory
rm -rf feature-extraction-suite/output-data/
docker compose -f feature-extraction-suite/docker/docker-compose.yml -p dt4h-onfhir-feast down -v