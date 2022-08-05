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


## Useful links:
- Original project: https://cloud.google.com/architecture/streaming-data-from-cloud-storage-into-bigquery-using-cloud-functions
- Code repo: https://github.com/GoogleCloudPlatform/solutions-gcs-bq-streaming-functions-python
- Firestore documentation: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/909a077e4565ac55ce9a6dd3e21e9991b1f76fce/firestore/cloud-client/snippets.py#L173-L189
- Blob (download_as_string): https://googleapis.dev/python/storage/latest/blobs.html






