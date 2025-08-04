#!/bin/bash
echo "Pulling onfhir-feast image from private SRDC repo..."
docker login nexus.srdc.com.tr:18445 --username tofhir --password-stdin < srdc-docker-registry-password.txt
docker pull nexus.srdc.com.tr:18445/srdc/onfhir-feast:latest
docker tag nexus.srdc.com.tr:18445/srdc/onfhir-feast:latest srdc/onfhir-feast:latest



