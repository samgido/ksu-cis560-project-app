from os import getenv
from flask import Flask
from dotenv import load_dotenv
import pyodbc 

if not load_dotenv():
    print("Environment file not found, see readme")
    exit(1)

def get_env_or_exit(env_name: str):
    val = getenv(env_name)

    if (val is None):
        print("Could not get env " + env_name)
        exit(1)

    return val

connection_string = get_env_or_exit("SQL_CONNECTION_STRING")

connection = pyodbc.connect(connection_string)

print(connection.getinfo(pyodbc.SQL_DATABASE_NAME))

cursor = connection.cursor()

cursor.execute("""
    select count(*) from test
""")

cursor.commit()

rows = cursor.fetchall()

for row in rows:
    print(row)

exit(0)

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <p>
        books
    </p>
    """

app.run(debug=True)
