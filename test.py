import pandas as pd 
from google.cloud import storage
from datetime import datetime, timedelta , timezone
import pytz
import json
import fsspec
import gcsfs


def send_data_gcs(bucket_name, data, file_name):
    gcs_uri = f'gs://{bucket_name}/{file_name}.csv'
    try:
        data.to_csv(gcs_uri, index=False) 
        print(f"DataFrame successfully uploaded to: {gcs_uri}")
        return True
    except Exception as e:
        print(f"Error uploading DataFrame to GCS: {e}")
        return False

bucket_name = 'gcs_trigger_function_report'

# Initialize Storage Object (Origin not destination)
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blobs = bucket.list_blobs() # Listed files in bucket

# Get current date in PTZ since I am in San Francisco
pacific_tz = pytz.timezone('America/Los_Angeles')
current_date_time = datetime.now(timezone.utc)
current_date_time_pacific = current_date_time.astimezone(pacific_tz)

def main():
    uri = f"gs://{bucket_name}/"
    rows_list = []
    columns_list = []
    try:
        for blob in blobs:
            file_name = blob.name
            if file_name.endswith('.json'):
                file_created_utc = blob.time_created
                file_created_pacific = file_created_utc.astimezone(pacific_tz)
                # Difference between current time and file creation
                time_difference = current_date_time_pacific - file_created_pacific
                hours_difference = round(time_difference.total_seconds() / 3600,0)
                # Check if file was created more than 24 hours ago
                if hours_difference > 24.0:
                    path = f'{uri}{file_name}'
                    data = pd.read_json(path, typ='series').to_frame(name='value')
                    rows = data.loc['Rows']
                    columns = data.loc['Columns']
                    rows_list.append(rows)
                    columns_list.append(columns)
                else:
                    pass
            else:
                print('Not JSON file received, not processing')
        # Transform capturd data for all files in a Pandas data FRame and then --> CSV
        report_df = pd.DataFrame({'Total Rows in Bucket':[sum(rows_list)],
                                'Total Columns in Bucket': [sum(columns_list)]
                                })
        print(report_df)

        # Upload to GCS bucket hourly report
        send_data_gcs('hourly_report_from_json_files', report_df, f'report_{current_date_time_pacific}')

    except Exception as e:
        print(f"Error processing files {e}") 

if __name__ == '__main__':
    main()


#TEST TO SEE I FIXED THE REPO CONNECTION

