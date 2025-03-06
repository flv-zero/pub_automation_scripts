import reusable_functions

from google.oauth2.credentials import Credentials
from google.cloud import bigquery
import json
import sys
import tkinter
from tkinter import filedialog, messagebox, ttk

# Prompting user for the configuration file
tkinter_root = tkinter.Tk()
tkinter_root.title('Google BigQuery automation by flvon')
info_frame = tkinter.Frame( tkinter_root, padx=5, pady=5 )
info_frame.grid( column=0, row=0, sticky='NSWE' )
logs_frame = tkinter.Frame( tkinter_root, padx=5, pady=5 )
logs_frame.grid( column=0, row=1, sticky='NSWE' )
info_label = ttk.Label( info_frame, foreground='gray', text='Google BigQuery query automation is running, don\'t close this window.\nIt exists so that you can find the program in your taskbar')
info_label.grid( column=0, row=0, sticky='W')
logs_label = ttk.Label( logs_frame, text='Execution information:' )
logs_label.grid( column=0, row=0, sticky='W' )
tkinter_root.update()
messagebox.showinfo( title='Google BigQuery query automation', message='A dialog will open for you to select a configuration\nfile with instructions to run the queries' )
# Reading configs
config_file = filedialog.askopenfilename( filetypes=[( 'JSON configuration files', '*.cfg' )] )
configs = json.load( open(config_file) ) 

project_id = configs['execution_project']
folder = configs['root_folder']

# Setting up logging
logger = reusable_functions.set_logging( root_path=folder, logging_level='INFO' )
logger.info( 'Google BigQuery script automations. Will run SQL scripts in folder set up in configuration file\n' )

logger.info( f'Running from following configuration file: {config_file}\n')

# Getting query file list and asking for confirmation
logger.info( 'Getting query list' )
try: query_list = reusable_functions.get_all_files_in_directory( folder=folder, file_extension='sql', sort_alphabetical=True )
except Exception as err: logger.info( err )

query_confirm_list = '\n'.join([ str(q) for q in query_list ])
logger.info( f'Running queries from path {folder}\nList of queries to be run:\n\n{query_confirm_list}\n')

confirmation_input = messagebox.askokcancel( title='Confirmation', message=f'Running queries from path {folder}\nDo you wish to run the following queries in this order?\n\n{query_confirm_list}' )
if confirmation_input is False:
	logger.info( 'Execution cancelled by user after reviewing query list' )
	sys.exit()

logger.info( 'User confirmed execution, starting now' )
# Getting GCP credentials
# If credentials have expired, try to refresh it using:
# refreshed_creds = Credentials(refresh_token=creds.refresh_token)

messagebox.showinfo( title='Select credentials file', message='Select you Google credentials file' )

auth_file = filedialog.askopenfilename( filetypes=[( 'Google credential files', '*.crd' )] )
scopes = ['openid', 'https://www.googleapis.com/auth/cloud-platform']

logger.info( 'Getting GCP credentials' )
creds = Credentials.from_authorized_user_file( auth_file, scopes=scopes)
bigquery_client = bigquery.Client( credentials=creds, project=project_id)

logger.info( 'Authentication finished, now running queries' )

for q in query_list:
	logger.info( f'Running query {q}' )
	logs_label['text'] += f'\nRunning query in file {q}.'
	tkinter_root.update()
	query_file = open( folder + '/' + q, encoding="utf-8")
	query = query_file.read()
	logger.debug( 'Query content' )
	logger.debug( query )
	parent_job = bigquery_client.query( query )

	try: parent_job.result()
	except Exception as err:
		logger.info( err )
		logger.info( 'Error when executing the query. Execution cancelled ')
		tkinter_root.destroy()
		sys.exit()

	child_jobs = list(bigquery_client.list_jobs( parent_job=parent_job.job_id )) # Returns the list of jobs within the parent job from newest to oldest in a list form
	for child in reversed(child_jobs): # Iterate in reverse to get oldest to newest
		child_job_id = child.job_id
		child_job = bigquery_client.get_job( job_id=child_job_id )
		affected_rows = child_job.num_dml_affected_rows
		first_word = child_job.query.split(' ', maxsplit=1)[0].lower() # Gets first word from the query statement in lowercase 

		if affected_rows:
			match first_word:
				case 'delete':
					logger.info( f'\tNumber of deleted rows: {affected_rows}' )
					logs_label['text'] += f'\n\tNumber of deleted rows: {affected_rows}'
					tkinter_root.update()
				case 'insert':
					logger.info( f'\tNumber of inserted rows: {affected_rows}' )
					logs_label['text'] += f'\n\tNumber of inserted rows: {affected_rows}'
					tkinter_root.update()
				case 'create':
					logger.info( f'\tNumber of rows in new table: {affected_rows}')
					logs_label['text'] += f'\n\tNumber of rows in new table: {affected_rows}'
					tkinter_root.update()
				case _:
					logger.info( '\tQuery did not have a DML statement' )
					logger.info( 'Query ran:\n{child_job.query}\n' )
					logs_label['text'] += '\n\tQuery did not have a DML statement'
					tkinter_root.update()
		else:
			logger.info( 'Query did not have a DML statement' )

logger.info( 'Execution finished with no errors' )
messagebox.showinfo( title='Execution finished', message='Execution finished successfuly' )
tkinter_root.destroy()