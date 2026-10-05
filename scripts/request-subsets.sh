#!/bin/bash
# Sends all 8 subset requests one after another and saves all responses, in order, to all_subset_responses.json

show_help() {
  cat << 'HELP'
Sends the 8 CKD subset requests one after another and saves all responses,
in order, to all_subset_responses.json.

Usage:
  ./scripts/request-subsets.sh <hostname/basePath> <dataset_id>

Parameters:
  hostname/basePath   Server host (with port if needed) and base path, without http://
  dataset_id          ID of the study1 dataset

Examples:
  ./scripts/request-subsets.sh localhost/dt4h/feast 8e3b598e-07a4-4a03-9b02-276b6d37f16c
  ./scripts/request-subsets.sh localhost:6095/onfhir-feast 8e3b598e-07a4-4a03-9b02-276b6d37f16c
  ./scripts/request-subsets.sh 192.168.1.10/my-base-path study1-dataset-id

Options:
  -h, --help          Show this help text
HELP
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
  exit 0
fi

if [ $# -ne 2 ]; then
  echo "Error: expected 2 parameters, got $#."
  echo
  show_help
  exit 1
fi

HOST_PATH="${1%/}"   # removes a trailing / if given
DATASET_ID="$2"

echo "Server:     http://$HOST_PATH"
echo "Dataset ID: $DATASET_ID"
echo

echo "[" > all_subset_responses.json

# Any CKD Male
echo '{"heading": "Any CKD Male", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "Male patients subset",
  "description": "Subset of the study1 dataset including only male patients",
  "query": {
    "name": "Only males",
    "language": "application/sql",
    "expression": "patient_demographics_gender = '\''male'\''"
  }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# Any CKD Female
echo '{"heading": "Any CKD Female", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "Female patients subset",
  "description": "Subset of the study1 dataset including only female patients",
  "query": {
    "name": "Only females",
    "language": "application/sql",
    "expression": "patient_demographics_gender = '\''female'\''"
  }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# CKD All Gender
echo '{"heading": "CKD All Gender", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "All CKD patients subset",
    "description": "Subset of the study1 dataset including all CKD patients",
    "query": {
        "name": "Only CKD patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''kidney_failure'\'' or ckd_severity_calculated_or_measured = '\''severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''moderate_to_severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''mild_to_moderate_decrease'\'')"
    }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# CKD Male
echo '{"heading": "CKD Male", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Male CKD patients subset",
    "description": "Subset of the study1 dataset including only male CKD patients",
    "query": {
        "name": "Only male CKD patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''kidney_failure'\'' or ckd_severity_calculated_or_measured = '\''severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''moderate_to_severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''mild_to_moderate_decrease'\'') and patient_demographics_gender = '\''male'\''"
    }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# CKD Female
echo '{"heading": "CKD Female", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Female CKD patients subset",
    "description": "Subset of the study1 dataset including only female CKD patients",
    "query": {
        "name": "Only female CKD patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''kidney_failure'\'' or ckd_severity_calculated_or_measured = '\''severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''moderate_to_severe_decrease'\'' or ckd_severity_calculated_or_measured = '\''mild_to_moderate_decrease'\'') and patient_demographics_gender = '\''female'\''"
    }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# No CKD All Gender
echo '{"heading": "No CKD All Gender", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "No CKD patients subset",
    "description": "Subset of the study1 dataset including only no CKD patients",
    "query": {
        "name": "Only no CKD patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''mildly_decreased'\'' or ckd_severity_calculated_or_measured = '\''normal_or_high'\'')"
    }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# No CKD Male
echo '{"heading": "No CKD Male", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Male no CKD patients subset",
    "description": "Subset of the study1 dataset including only no CKD male patients",
    "query": {
        "name": "Only no CKD male patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''mildly_decreased'\'' or ckd_severity_calculated_or_measured = '\''normal_or_high'\'') and patient_demographics_gender = '\''male'\''"
    }
}' >> all_subset_responses.json
echo "}," >> all_subset_responses.json

# No CKD Female
echo '{"heading": "No CKD Female", "response":' >> all_subset_responses.json
curl -sS --request POST \
  --url "http://$HOST_PATH/api/Dataset/$DATASET_ID/\$subset" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Female no CKD patients subset",
    "description": "Subset of the study1 dataset including only no CKD female patients",
    "query": {
        "name": "Only no CKD female patients",
        "language": "application/sql",
        "expression": "ckd_severity_calculated_or_measured is not NULL and (ckd_severity_calculated_or_measured = '\''mildly_decreased'\'' or ckd_severity_calculated_or_measured = '\''normal_or_high'\'') and patient_demographics_gender = '\''female'\''"
    }
}' >> all_subset_responses.json
echo "}" >> all_subset_responses.json

echo "]" >> all_subset_responses.json

cat all_subset_responses.json
echo
echo "All requests finished. Responses saved to all_subset_responses.json"