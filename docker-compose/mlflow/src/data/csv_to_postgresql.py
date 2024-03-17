import psycopg2
import csv
from io import StringIO
from pathlib import Path  # Import Path from pathlib
import sys

# Add the parent directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))


# Load database connection information from a configuration file
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

# List of commands for table creation
CREATE_TABLE_COMMANDS = []

# Add the command to create the `dataset` table
CREATE_TABLE_COMMANDS.append(
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
    lat FLOAT,  -- Retained as FLOAT for geographical coordinates
    long FLOAT, -- Retained as FLOAT for geographical coordinates
    hour VARCHAR(255),
    nb_victim VARCHAR(255),
    nb_vehicules VARCHAR(255)
    );
    """
)

# Calculate the absolute path to the CSV file
abs_path = str(Path().absolute())
csv_file_path = f"{abs_path}/data/preprocessed/dataset.csv"  # Ensure this path exists

def create_tables(conn):
    """Creates tables in the database based on CREATE_TABLE_COMMANDS."""
    cursor = conn.cursor()
    for command in CREATE_TABLE_COMMANDS:
        cursor.execute(command)
    conn.commit()
    cursor.close()

def insert_csv_to_db(conn, file_path, table_name):
    """Inserts data from a CSV file into the corresponding table, using semicolon as delimiter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        # Use StringIO to store the CSV content
        buffer = StringIO(f.read())
        buffer.seek(0)  # Go to the start of the stream

    cursor = conn.cursor()
    try:
        # Use copy_expert to efficiently copy data into the database
        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''", buffer)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data from {file_path}: {e}")
    finally:
        cursor.close()
        buffer.close()

def main():
    """Main function that establishes connection to the database, creates tables, and inserts data."""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    
    # Create the tables
    create_tables(conn)
    
    # Insert data from the CSV file into the `dataset` table
    insert_csv_to_db(conn, csv_file_path, "dataset")
    
    conn.close()

if __name__ == '__main__':
    main()
