from fastapi import FastAPI, HTTPException, Body, Request, status
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT  # config import
from fastapi.responses import JSONResponse
from io import StringIO
import os
import shutil
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()

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
async def create_table_endpoint():
    # Your CREATE TABLE command should be updated accordingly
    create_table_command = """
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
    user_create_command = """
        CREATE TABLE IF NOT EXISTS user_tab (
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            permission VARCHAR(50) NOT NULL CHECK (permission IN ('Admin', 'Superuser'))
        );
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(create_table_command)
        cursor.execute(user_create_command)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {"message": "Table created successfully"}

@app.get("/init_users")
def init_users():
    users = [
        ("Test_admin", "Test_admin_password", "Admin"),
        ("Test_superuser", "Test_superuser_password", "Superuser")
    ]
    insert_command = """
        INSERT INTO user_tab (Username, Password, Permission) VALUES (%s, %s, %s)
        ON CONFLICT (Username) DO NOTHING;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for user in users:
            cursor.execute(insert_command, user)
        conn.commit()
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Failed to initialize user table"})
    finally:
        cursor.close()
        conn.close()
    
    return {"message": "User table initialized successfully"}


class ManageUsersRequest(BaseModel):
    username: str
    password: str
    action: str
    target_username: str = ''
    target_password: str = ''
    target_permission: str = ''


@app.post("/admin/manage_users")
async def manage_users(request_data: ManageUsersRequest):
    data = request_data.dict()
    username = data['username']
    password = data['password']
    action = data['action']
    target_username = data['target_username']
    target_password = data['target_password']
    target_permission = data['target_permission']

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing credentials")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Permission FROM user_tab WHERE Username = %s AND Password = %s", (username, password))
        permission_record = cursor.fetchone()

        if not permission_record or permission_record[0].lower() != 'admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

        if action == 'add':
            cursor.execute("INSERT INTO user_tab (Username, Password, Permission) VALUES (%s, %s, %s)", (target_username, target_password, target_permission))
        elif action == 'delete':
            cursor.execute("DELETE FROM user_tab WHERE Username = %s", (target_username,))
        elif action == 'modify':
            cursor.execute("UPDATE user_tab SET Password = %s, Permission = %s WHERE Username = %s", (target_password, target_permission, target_username))
        else:
            raise ValueError("Invalid action specified")

        conn.commit()
        message = f"Action '{action}' completed successfully for user: {target_username}"
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error executing '{action}': {str(e)}")
    finally:
        cursor.close()
        conn.close()

    return {"message": message}





@app.post('/insert_csv')
def insert_csv_endpoint(request: Request):
    file_path = request.args.get('file_path', CSV_FILE_PATH)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            buffer = StringIO(f.read())
            buffer.seek(0)
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
        destination_path = os.path.join(DESTINATION_FOLDER, os.path.basename(file_path))
        shutil.move(file_path, destination_path)
        message = f"File moved to {destination_path} successfully."
    except Exception as e:
        message = f"Error moving file: {str(e)}"
    
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

#@app.post('/data')
#def execute_query(data: QueryData):
#    # Basic validation for the query input
#    if not data.query:
#        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder({'error': 'No query provided'}))#
#
#   try:
#        conn = get_db_connection()
#        cursor = conn.cursor(cursor_factory=RealDictCursor)
#       cursor.execute(data.query)  # Execute the query provided by the user
#        fetched_data = cursor.fetchall()
#        cursor.close()
#        conn.close()
#        return fetched_data
#    except Exception as e:
#        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder({'error': 'Failed to execute query', 'details': str(e)}))