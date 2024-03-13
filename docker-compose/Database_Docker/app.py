import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor
import shutil
import os
from io import StringIO
import os

### NEW
from fastapi import FastAPI, Body, Request
from fastapi.encoders import jsonable_encoder
app = FastAPI()

### END NEW

DB_HOST = os.environ.get('POSTGRES_HOST') 
DB_NAME = os.environ.get('POSTGRES_DB') 
DB_USER = os.environ.get('POSTGRES_USER') 
DB_PASS = os.environ.get('POSTGRES_PASSWORD') 
DB_PORT = os.environ.get('POSTGRES_PORT') 


CSV_FILE_PATH = "dataset.csv"  # Ensure this path points to your CSV file
DESTINATION_FOLDER = "./Transferred/"

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


@app.get("/create_database")
def create_database_endpoint():
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if cursor.fetchone() is None:
        try:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            message = "Database " + DB_NAME + " created successfully."
        except Exception as e:
            message = "An error occurred: " + str(e)
    else:
        message = "Database " + DB_NAME + " already exists."

    cursor.close()
    conn.close()
    return {"message": message}

@app.get('/create_table')
def create_table_endpoint():
    # Your CREATE TABLE command should be updated accordingly
    msg = create_table()
    return {"message": msg}



def create_table():    
    create_table_command = (
        """
        CREATE TABLE IF NOT EXISTS dataset (
        place VARCHAR(255),
        catu VARCHAR(255),
        grav VARCHAR(255),
        sexe VARCHAR(255),
        secu1 VARCHAR(255),
        year_acc VARCHAR(255),
        victim_age VARCHAR(255),
        catv VARCHAR(255),
        obsm VARCHAR(255),
        motor VARCHAR(255),
        catr VARCHAR(255),
        circ VARCHAR(255),
        surf VARCHAR(255),
        situ VARCHAR(255),
        vma VARCHAR(255),
        jour VARCHAR(255),
        mois VARCHAR(255),
        lum VARCHAR(255),
        dep VARCHAR(255),
        com VARCHAR(255),
        agg_ VARCHAR(255),
        int VARCHAR(255),
        atm VARCHAR(255),
        col VARCHAR(255),
        lat FLOAT,
        long FLOAT,
        hour VARCHAR(255),
        nb_victim VARCHAR(255),
        nb_vehicules VARCHAR(255)
        );
        """
    )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(create_table_command)
    conn.commit()
    cursor.close()
    conn.close()
    return "Table created successfully"

@app.post('/insert_csv')
def insert_csv_endpoint(request: Request):
    file_path = request.args.get('file_path', CSV_FILE_PATH)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    with open(file_path, 'r', encoding='utf-8') as f:
        buffer = StringIO(f.read())
        buffer.seek(0)
        try:
            cursor.copy_expert(f"COPY dataset FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''", buffer)
            conn.commit()
            message = "Data inserted successfully from CSV."
        except Exception as e:
            conn.rollback()
            message = "Error inserting data from CSV: " + str(e)
        finally:
            cursor.close()
    conn.close()
    
    return {"message": message}

@app.post('/move_csv')
def move_csv_endpoint(request: Request):
    file_path = request.args.get('file_path', CSV_FILE_PATH)
    try:
        shutil.move(file_path, os.path.join(DESTINATION_FOLDER, os.path.basename(file_path)))
        message = "File moved to " + DESTINATION_FOLDER + " successfully."
    except Exception as e:
        message = "Error moving file: " + str(e)
    
    return {"message": message}

@app.get('/data_test')
def get_data_():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM dataset Limit 3;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonable_encoder(data)

@app.post('/data')
async def get_data(request: Request):
    data = await request.json()  # Get data from POST request
    query = data['query']  # Extract query from the data

    # Basic validation for the query input
    if not query:
        return jsonable_encoder({'error': 'No query provided'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)  # Execute the query provided by the user
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonable_encoder(data)
    except Exception as e:
        return jsonable_encoder({'error': 'Failed to execute query', 'details': str(e)}), 500


# if __name__ == '__main__':
#     if not os.path.exists(DESTINATION_FOLDER):
#         os.makedirs(DESTINATION_FOLDER)
#     #create_table()
#     app.run(debug=True,host='0.0.0.0', port=5000)
