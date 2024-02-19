#!/bin/bash

docker compose -f feature-extraction-suite/docker/docker-compose.yml --project-directory ./ -p dt4h-feast up -d
