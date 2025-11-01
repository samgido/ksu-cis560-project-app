# KSU CIS560 project app

## Setup
Create a .env file in the base directory definining some variables to establish a connection with the database. Contents should look something like this
```
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=<server_name>;Database={<database_name>};Encrypt=yes;TrustServerCertificate=no;Authentication=ActiveDirectoryInteractive"
```
More info [here](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/python-sql-driver-pyodbc-quickstart?view=sql-server-ver17&tabs=sql-server)

## Usage
To run project to http://localhost:5000
```
uv run ./main.py
```
