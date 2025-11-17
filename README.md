# KSU CIS560 project app

## Setup
First, download [database_creation.zip](https://github.com/user-attachments/files/23589062/database_creation.zip), run the .sql script then the python script to load our mock data into a database. 

Next, create a .env file in the base directory with the SQL connection string in it, contents should look something like this
```
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=<server_name>;Database={<database_name>}"
```
An example connection string for LocalDB;
```
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDB;Database={WideWorldImporters}"
```
More info about connection string [here](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/python-sql-driver-pyodbc-quickstart?view=sql-server-ver17&tabs=sql-server#create-a-new-file)

## Usage
To run project to http://localhost:5000
```
uv run ./main.py
```
