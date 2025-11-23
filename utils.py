from typing import Optional, List, Any
from pathlib import Path
from flask import render_template
import pyodbc
import dotenv 
import os 

PAGE_SIZE = 32

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

def all_or_none(l: List[Any]) -> Optional[List[Any]]: 
    return l if all(l) else None # return none if any element is none

def get_analytics_query_names():
    IGNORE = ["analytics_input"]

    templates_dir = Path("templates/analytics")

    if not templates_dir.exists():
        return None

    if not templates_dir.is_dir():
        return None

    query_names = [x.stem for x in templates_dir.iterdir() if x.is_file() and x.stem not in IGNORE]
    return query_names

# snake_case -> Snake case
def snake_case_to_proper(s: str):
    s = s.replace('_', ' ')
    s = s[0].capitalize() + s[1:]

    return s
