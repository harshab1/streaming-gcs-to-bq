'''This Cloud Function is responsible for:
- Parsing and validating new files added to Cloud Storage
- Checking for duplications
- Inserting files content into Bigquery
- Logging ingestion status into Cloud Firestore and Stackdriver
- Publishing a message to either an error or success topic in Cloud Pub/Sub
'''

import logging
import json
import os
import traceback
from datetime import datetime
import pytz

from google.cloud import firestore
from google.cloud import storage
from google.cloud import bigquery
from google.api_core import retry
from google.cloud import pubsub_v1

DB = firestore.Client()
CS = storage.Client()
BQ = bigquery.Client()
BQ_DATASET = 'dataset_files_sink_json'
BQ_TABLE = 'table_sink'
PS = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv('GCP_PROJECT')
SUCCESS_TOPIC = 'projects/%s/topics/%s' % (PROJECT_ID, 'streaming_success_topic')
ERROR_TOPIC = 'projects/%s/topics/%s' % (PROJECT_ID, 'streaming_error_topic')


def streaming(data, context):
    '''This function is executed whenever a file is added to Cloud Storage. Flow of logic in this function:
    -  Checks if the data is already ingested
    - If yes, handles duplication
    - Else, Ingested into BQ and successful message is published to Pub/Sub streaming_error_topic topic
    - In case of exception, unsuccessful message is published to Pub/Sub streaming_success_topic
     '''
    bucket_name = data['bucket']
    file_name = data['name']
    db_ref = DB.document(u'streaming_files/%s' % file_name)
    if _was_already_ingested(db_ref):
        _handle_duplication(db_ref)
    else:
        try:
            _insert_into_bigquery(bucket_name, file_name)
            _handle_success(db_ref)
        except Exception:
            _handle_error(db_ref)


def _was_already_ingested(db_ref):
    status = db_ref.get()
    if status.exists:
        return True
    else:
        return False

def _handle_duplication(db_ref):
    dups = [_now()]
    data = db_ref.get().to_dict()
    if 'duplication_attempts' in data:
        dups.extend(data['duplication-attempts'])
    db_ref.update({
        'duplication_attempts': dups
    })
    logging.warning('Duplication attempt while streaming file \'%s\'' % db_ref.id)

def _now():
    datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

def _insert_into_bigquery(bucket_name, file_name):
    blob = CS.get_bucket(bucket_name).blob(file_name)
    row = json.loads(blob.download_as_string())
    table = BQ.dataset(BQ_DATASET).table(BQ_TABLE)
    errors = BQ.insert_rows_json(table, 
                                json_row=[row], 
                                row_ids=[file_name],
                                retry=retry.Retry(deadline=30))
    # if errors != []:
    #     raise BigQueryError(errors)

def _handle_success(db_ref):
    message = 'File \'%s\' streamed into BigQuery' % db_ref.id
    doc = {
        u'success': True,
        u'when': _now()
    }
    db_ref.set(doc)
    PS.publish(SUCCESS_TOPIC, message.emcode('utf-8', file_name=db_ref.id))
    logging.info(message)

def _handle_error(db_ref):
    message = 'Error streaming file \'%s\. Cause: %s' % (db_ref.id, traceback.format_exec())
    doc = {
        u'success': False,
        u'error_message': message,
        u'when': _now()
    }
    db_ref.set(doc)
    PS.publish(ERROR_TOPIC, message.encode('utf-8'), file_name=db_ref.id)
    logging.error(message)

# class BiqQueryError(Exception):




