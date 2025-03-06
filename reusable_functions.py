import os
import logging
import datetime
from pathlib import Path

def change_working_directory_to_script_directory():
	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(dname)
		
def get_all_files_in_directory( folder, file_extension=None, sort_alphabetical=True ):
	if file_extension:
		file_extension = file_extension.lower()
		file_list = [ file_name for file_name in os.listdir( folder ) if os.path.isfile( os.path.join(folder, file_name) ) and file_name.lower().endswith('.' + file_extension) ]
	else:
		file_list = [ file_name for file_name in os.listdir( folder ) if os.path.isfile( os.path.join(folder, file_name) ) ]

	if sort_alphabetical: file_list = sorted( file_list )
	return file_list

def set_logging( root_path, filename_timestamp_level='second', log_base_filename='execution_log', logging_level='INFO' ):
	#Setting logging path and file
	now = datetime.datetime.now()
	match filename_timestamp_level:
		case 'year':
			dt = now.strftime( "%Y" )
		case 'month':
			dt = now.strftime( "%Y%m" )
		case 'day':
			dt = now.strftime( "%Y%m%d" )
		case 'hour':
			dt = now.strftime( "%Y%m%d_%H" )
		case 'minute':
			dt = now.strftime( "%Y%m%d_%H%M" )
		case _:
			dt = now.strftime( "%Y%m%d_%H%M%S" )
			
	log_folder = os.path.join( root_path, 'logs' )
	log_file_path = os.path.join( log_folder, dt + '_' + log_base_filename + '.log' )

	# Creating logging folder if it doesn't exist
	Path( log_folder ).mkdir( parents=True, exist_ok=True )
	# Creating logging file if it doesn't exist
	file = open( log_file_path, 'a' )
	file.close()

	# Setting loggers
	logger = logging.getLogger( 'Logger' )
	logger.setLevel( 'DEBUG' )
	formatter = logging.Formatter( fmt="{asctime} - {levelname} - {message}"
								  ,style="{"
								  ,datefmt="%Y-%m-%d %H:%M:%S"
								  )

	console_handler = logging.StreamHandler()
	console_handler.setLevel( logging_level )
	console_handler.setFormatter( formatter )
	logger.addHandler( console_handler )

	file_handler = logging.FileHandler( filename=log_file_path, mode='a', encoding='utf-8' )
	file_handler.setLevel( logging_level )
	file_handler.setFormatter( formatter )
	logger.addHandler( file_handler )

	return logger