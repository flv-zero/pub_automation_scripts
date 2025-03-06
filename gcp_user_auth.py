import reusable_functions
from google.oauth2.credentials import Credentials
from google.cloud import bigquery
import datetime
import json

# Constants
REQ_SCOPES = ['openid', 'https://www.googleapis.com/auth/cloud-platform']
AUTH_FILE = 'credentials.cfg'
CONFIG_FILE = 'configs.cfg'

# Changing working directory to this script's directory
reusable_functions.change_working_directory_to_script_directory()

# Reading configs
configs = json.load( open(CONFIG_FILE) )
execution_project = configs['execution_project']

tablepath = 'project.dataset.table_name'
example_variable_1 = '2024-01-01'
example_variable_2 = 'This is a string'

# Getting GCP credentials
# If credentials have expired, try to refresh it using:
# refreshed_creds = Credentials(refresh_token=creds.refresh_token)
creds = Credentials.from_authorized_user_file( AUTH_FILE, scopes=REQ_SCOPES)
bigquery_client = bigquery.Client( credentials=creds, project=execution_project)

job = bigquery_client.query( f"""insert into {tablepath} select cast( '{example_variable_1}' as date ), '{example_variable_2}'""")
job_result = job.result() # Will raise an error if the query is results in an error