# The Library Domain <image src="/static/favicon.ico"></image>
By Sam Gido, Ryan Black, Aidan McGlynn 

For CIS560 at KSU

## Setup
1. Run both scripts in the setup_scripts directory to create the database, schema and stored procedures
2. Unzip this folder [database_creation.zip](https://github.com/user-attachments/files/23897051/database_creation.zip) and run the python script, this will load the mock data into the database
3. Create a file called '.env' in the root directory of the repository with a SQL connection string in it, contents should look something like this
```
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=<server_name>;Database={<database_name>}"
```
An example connection string for LocalDB:
```
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDB;Database={WideWorldImporters}"
```
More info about connection string [here](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/python-sql-driver-pyodbc-quickstart?view=sql-server-ver17&tabs=sql-server#create-a-new-file)

## Usage
To run project to http://localhost:5000
```
uv run ./main.py
```
