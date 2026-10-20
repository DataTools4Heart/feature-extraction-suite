#!/bin/bash

docker compose -f feature-extraction-suite/docker/repofyr/docker-compose-repofyr.yml --project-directory ./ -p dt4h-repofyr-feast up -d