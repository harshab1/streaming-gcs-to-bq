# streaming-gcs-to-bq
Streaming data from Cloud Storage into BigQuery using Cloud Functions

## GCP Services:
### Cloud Functions: 
It is an event-driven, serverless compute platform, which provides automatic scaling, high availability and fault tolerance with no servers to provision, manage, update, or patch.

### Firestore: 
It is a NoSQL serverless document database that simplifies storing, syncing, and querying data for mobile, web and IoT apps at global scale. 


![Architecture](architecture.svg)
## Steps:
As seen in the Architecture diagram, the pipeline consists of following steps:
1. JSON files are uploaded to the `FILES_SOURCE` Cloud Storage Bucket 
2. This event triggers the `streaming` Cloud Function
3. Data is parsed and inserted into BigQuery
4. The ingestion status is logged into Firestore and Cloud Logging
5. A message is published in one of the following Pub/Sub topics:
- `streaming_success_topic`
- `streaming_error_topic`
6. Depending on the results, Cloud Functions moves the JSON file from the `FILES_SOURCE` bucket to one of the following buckets:
- `FILES_ERROR`
- `FILES_SUCCESS`

## Objectives:
1. Create a Cloud Storage bucket to store the JSON files
2. Create a BQ dataset and table to stream the data in to
3. Configure a Cloud Function to trigger whenever files are added to the bucket
4. Set up Pub/Sub topics
5. Configure additional functions to handle function output
6. Test the streaming pipeline
7. Configure Cloud Monitoring to alert on any unexpected behaviors

## Implementation steps:
1. Project setup:
- Create a project: `gcloud projects create PROJECT_ID --organization=ORGANIZATION_ID --folder=FOLDER_ID`
- Enable billing, check status: `gcloud beta billing projects describe PROJECT_ID`
- Enable Cloud Functions and Cloud Build APIs
2. Setting up the environment:
- In the Cloud Shell, make sure project is set to the correct one, using `gcloud config set project PROJECT_ID`
- Set the default compute zone, using `REGION=us-east1`
3. Creating streaming source and destination sinks:
- Create source Cloud Storage bucket with a timestamp, using `gsutil mb -c regional -l ${REGION} gs://${FILE_SOURCE}` where `FILES_SOURCE=${DEVSHELL_PROJECT_ID}-files-source-json-$(date +%s)`
- Create BigQuery dataset using `bq mk dataset_files_sink_json` table using the schema in `schema.json` file with command `bq mk dataset_files_sink_json.table_sink schema.json`
4. Streaming data into Big Query:
- Setting up the streaming Cloud Function: 
    * This function listens to new files added to Cloud Storage source bucket and triggers a process that does the following:
        * Parses and validates the file
        * Checks for duplications
        * Inserts the file's content into BigQuery
        * Logs the ingestion status in Firestore and Logging
        * Publishes a message to either an error or success topic in Pub/Sub
    * Creating a Cloud Storage bucket to stage the functions during deployment, using `gsutil mb -c regional -l us-east1 gs://${FUNCTIONS_BUCKET}` where `FUNCTIONS_BUCKET=${DEVSHELL_PROJECT_ID}-functions-$(date +%s)`
    * Deploy the streaming function, using `gcloud functions deploy streaming --region=${REGION} --source=./cloud-functions/streaming --runtime=python37 --stage-bucket=${FUNCTIONS_BUCKET} --trigger-bucket=${FILES_SOURCE}`
    * Check whether the function is deployed, using `gcloud functions describe streaming --region=${REGION}`
- Provision Pub/SUb topics to handle success and error in streaming data using `gcloud pubsub topics create ${STREAMING_SUCCESS_TOPIC}` and `gcloud pubsub topics create ${STREAMING_ERROR_TOPIC}`, where `STREAMING_SUCCESS_TOPIC=streaming_success_topic` and `STREAMING_ERROR_TOPIC=streaming_error_topic` 
- Setting up the Firestone database
    * On the console, Go to Firestore, Choose Cloud Firestore mode, Select Native mode, Select nam5(United States) location
- Handling streaming errors
    * 

## Useful links:
- Original project: https://cloud.google.com/architecture/streaming-data-from-cloud-storage-into-bigquery-using-cloud-functions
- Code repo: https://github.com/GoogleCloudPlatform/solutions-gcs-bq-streaming-functions-python
- Firestore documentation: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/909a077e4565ac55ce9a6dd3e21e9991b1f76fce/firestore/cloud-client/snippets.py#L173-L189
- Blob (download_as_string): https://googleapis.dev/python/storage/latest/blobs.html






