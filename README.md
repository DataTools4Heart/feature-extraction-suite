# DataTools4Heart Feature Extraction Suite
This repository contains feature extraction definitions that process patient data represented in the DT4H CDM and tranform it to a tabular format, which would be used to train ML models. Feature extraction process is realized via four main concepts, namely **populations**, **feature groups**, **feature sets** and **pipelines**.

Broadly, the feature extraction suite extracts patients' data from the FHIR patient data repository based on population definition. 

Then, feature groups' main aim is to extract a group of raw features for specific healthcare resources such as conditions, medications, lab measurements, etc. For each feature group a timeseries table is created such that
  * Each record specified matching to the FHIR query of the feature group will be mapped as a row in the table
  * Each feature defined in the feature group will be converted a column in the table

In the next step, feature sets work on the timeseries data generated by the feature groups to extract the final tabular dataset. Feature sets allow the following dataset manipulations:
  * Identification of reference time points that would lead to data points in the final dataset
  * Grouping data based on the reference time points in configurable time periods 
  * Applying aggregations on the grouped data

Pipelines are used to associate feature sets and populations. This indicates that a dataset, as configured by the feature sets, will be generated for the specified population in the pipeline.

## Current Definitions
When looked into the current definitions, the feature group defined so far are mainly driven by the DT4H CDM profiles, vital signs, encounters, electrocardiographs, medications, etc. 

The _study-features.json_ contains the input (independent) and output (dependent) variables that are required for the sub-study 1, which is "Medication prescription in patients with acute heart failure and chronic kidney disease or hyperkalaemia".

