#!/bin/bash
echo "Pulling onfhir-feast image from private SRDC repo..."
docker login docker.srdc.com.tr --username tofhir --password-stdin < srdc-docker-registry-password.txt
docker pull docker.srdc.com.tr/srdc/onfhir-feast:latest
docker tag docker.srdc.com.tr/srdc/onfhir-feast:latest srdc/onfhir-feast:latest



