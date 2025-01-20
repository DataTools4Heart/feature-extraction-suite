#!/bin/bash

docker compose -f feature-extraction-suite/docker/docker-compose.yml --project-directory ./ run onfhir-feast-cli extract-p -jobId feature-extraction-job-test -name study1

# Interactive feast
docker compose -f feature-extraction-suite/docker/docker-compose.yml --project-directory ./ run -it onfhir-feast-cli -it