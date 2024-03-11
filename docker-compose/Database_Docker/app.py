from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor
import shutil
import os
from io import StringIO
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT  # Updated import

app = Flask(__name__)

CSV_FILE_PATH = "dataset.csv"  # Ensure this path points to your CSV file
DESTINATION_FOLDER = "./Transferred/"

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

@app.route('/create_database', methods=['GET'])
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
    return jsonify({"message": message})

@app.route('/create_table', methods=['GET'])
def create_table_endpoint():
    # Your CREATE TABLE command should be updated accordingly

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
    
    return jsonify({"message": "Table created successfully"})

@app.route('/insert_csv', methods=['POST'])
def insert_csv_endpoint():
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
    
    return jsonify({"message": message})

@app.route('/move_csv', methods=['POST'])
def move_csv_endpoint():
    file_path = request.args.get('file_path', CSV_FILE_PATH)
    try:
        shutil.move(file_path, os.path.join(DESTINATION_FOLDER, os.path.basename(file_path)))
        message = "File moved to " + DESTINATION_FOLDER + " successfully."
    except Exception as e:
        message = "Error moving file: " + str(e)
    
    return jsonify({"message": message})

@app.route('/data_test', methods=['GET'])
def get_data_():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM dataset Limit 3;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/data', methods=['POST'])
def get_data():
    data = request.get_json()  # Get data from POST request
    query = data.get('query')  # Extract query from the data

    # Basic validation for the query input
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)  # Execute the query provided by the user
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Failed to execute query', 'details': str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(DESTINATION_FOLDER):
        os.makedirs(DESTINATION_FOLDER)
    app.run(debug=True,host='0.0.0.0', port=5000)
