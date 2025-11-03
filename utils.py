from flask import render_template
import pyodbc
import dotenv 
import os 

def get_env_or_exit(env_name: str):
    val = os.getenv(env_name)

    if (val is None):
        print("Could not get env variable: " + env_name)
        print("See readme")
        exit(1)

    return val

def create_database_connection():
    conn_str = get_env_or_exit("SQL_CONNECTION_STRING")

    return pyodbc.connect(conn_str)

def check_dotenv():
	if not dotenv.load_dotenv():
		print("Environment file not found, see readme")
		exit(1)

def render_success_failure(message):
	return render_template('success_failure.html', message=message)
