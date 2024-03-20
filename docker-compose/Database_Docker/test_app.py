import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from unittest.mock import patch, MagicMock, mock_open, call
from fastapi.exceptions import HTTPException
from app import create_database, get_db_connection, create_table, init_users, insert_csv, move_csv,initialize_application, CSV_FILE_PATH, DESTINATION_FOLDER, execute_user_action, app  
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT 
import os

 #Test successful database connection
@patch('app.psycopg2.connect')
def test_get_db_connection_success(mock_connect):
    # Setup a mock connection object
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    # Attempt to get the database connection
    conn = get_db_connection()

    # Verify that a connection was attempted and the mock connection was returned
    mock_connect.assert_called_once()
    assert conn == mock_conn, "Expected get_db_connection to return a mock database connection."

# Test failed database connection
@patch('app.psycopg2.connect')
def test_get_db_connection_failure(mock_connect):
    # Simulate a connection failure by raising an exception
    mock_connect.side_effect = Exception("Failed to connect to database")

    # Verify that the function raises an exception when connection fails
    with pytest.raises(Exception, match="Failed to connect to database"):
        get_db_connection()


@patch('app.psycopg2.connect')
def test_create_database_not_exist(mock_connect):
    mock_connect.return_value.cursor.return_value.fetchone.return_value = None
    response = create_database()
    assert response["message"] == f"Database {DB_NAME} created successfully."

@patch('app.psycopg2.connect')
def test_create_database_already_exists(mock_connect):
    mock_connect.return_value.cursor.return_value.fetchone.return_value = (1,)
    response = create_database()
    assert response["message"] == f"Database {DB_NAME} already exists."

@patch('app.psycopg2.connect')
def test_create_database_creation_fails(mock_connect):
    mock_connect.return_value.cursor.return_value.fetchone.return_value = None
    mock_connect.return_value.cursor.return_value.execute.side_effect = [None, Exception("Creation failed")]
    response = create_database()
    assert "An error occurred: Creation failed" in response["message"]

# Test Table Creation
@patch('app.get_db_connection')
def test_create_table_success(mock_get_db_connection):
    # Setup mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Execute the function under test
    response = create_table()

    # Verify that the commit was called to confirm table creation
    mock_conn.commit.assert_called_once()

    # Check that cursor.execute was called with the expected SQL commands
    # by verifying key components rather than matching the entire text exactly.
    sql_commands = [
        "CREATE TABLE IF NOT EXISTS dataset",
        "CREATE TABLE IF NOT EXISTS user_tab"
    ]
    for sql_command in sql_commands:
        found = any(sql_command in call.args[0] for call in mock_cursor.execute.call_args_list)
        assert found, f"SQL command for creating table not found: {sql_command}"

# Check the function's success message
    assert response["message"] == "Tables created successfully", "Expected message to indicate successful table creation."

@patch('app.get_db_connection')
def test_create_table_failure(mock_get_db_connection):
    # Setup mock connection and cursor to simulate a failure during table creation
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Failed to create tables")

    # Execute the function under test and verify the failure behavior
    response = create_table()

    # Ensure the function handled the exception by rolling back
    mock_conn.rollback.assert_called_once()

    # Check the function's failure message
    assert "Failed to create tables" in response["message"], "Expected message to reflect the failure in table creation."

# Test successful user table initialization  
@patch('app.get_db_connection')
def test_init_users_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    response = init_users()

    # Verify that cursor.execute was called the correct number of times with the expected SQL command
    assert mock_cursor.execute.call_count == 2, "Expected cursor.execute to be called twice for the two user records."
    sql_command_start = "INSERT INTO user_tab"
    mock_calls = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert all(sql_command_start in call for call in mock_calls), "Expected SQL command to insert user records not found in executed queries."

    assert response["message"] == "User table initialized successfully", "Expected successful initialization message."

# Test failure during user table initialization
@patch('app.get_db_connection')
def test_init_users_failure(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Failed to insert user record")
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    response = init_users()

    # Ensure the function captures the exception and returns an appropriate failure message
    assert "Failed to initialize user table" in response["message"], "Expected failure message upon exception."

    # Verify that the transaction is rolled back in case of an exception
    mock_conn.rollback.assert_called_once(), "Expected a rollback after a failure."

# Test successful CSV data insertion
@patch("builtins.open", new_callable=mock_open, read_data="header1,header2\nvalue1,value2")
@patch("app.get_db_connection")
def test_insert_csv_success(mock_get_db_connection, mock_file):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    response = insert_csv(CSV_FILE_PATH)

    # Verify that the COPY command was executed
    mock_cursor.copy_expert.assert_called_once()
    assert response["message"] == "Data inserted successfully from CSV.", "Expected successful insertion message."

# Test failure during CSV data insertion
@patch("builtins.open", new_callable=mock_open, read_data="header1,header2\nvalue1,value2")
@patch("app.get_db_connection")
def test_insert_csv_failure(mock_get_db_connection, mock_file):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.copy_expert.side_effect = Exception("Failed to insert data")
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    response = insert_csv(CSV_FILE_PATH)

    # Ensure the function captures the exception and returns an appropriate failure message
    assert "Error inserting data from CSV" in response["message"], "Expected failure message upon exception."

    # Verify that the transaction is rolled back in case of an exception
    mock_conn.rollback.assert_called_once(), "Expected a rollback after a failure."


# Test successful CSV file move
@patch("app.shutil.move")
def test_move_csv_success(mock_move):
    destination_path = os.path.join(DESTINATION_FOLDER, os.path.basename(CSV_FILE_PATH))

    response = move_csv(CSV_FILE_PATH)

# Verify shutil.move was called correctly
    mock_move.assert_called_once_with(CSV_FILE_PATH, destination_path)
    assert response["message"] == f"File moved to {destination_path} successfully.", "Expected successful move message."

# Test failure during CSV file move
@patch("app.shutil.move")
def test_move_csv_failure(mock_move):
    mock_move.side_effect = Exception("Failed to move file")

    response = move_csv(CSV_FILE_PATH)

    # Ensure the function captures the exception and returns an appropriate failure message
    assert "Error moving file: Failed to move file" in response["message"], "Expected failure message upon exception."


# Test that initialize_application calls the necessary functions in the correct order
@patch("app.move_csv")
@patch("app.insert_csv")
@patch("app.init_users")
@patch("app.create_table")
@patch("app.create_database")
def test_initialize_application(mock_create_database, mock_create_table, mock_init_users, mock_insert_csv, mock_move_csv):
    initialize_application()

    # Verify that each function was called exactly once
    mock_create_database.assert_called_once()
    mock_create_table.assert_called_once()
    mock_init_users.assert_called_once()
    mock_insert_csv.assert_called_once()
    mock_move_csv.assert_called_once()

 # Define the Pydantic model inline for simplicity; replace with actual import in your code
class ManageUsersRequest(BaseModel):
    action: str
    current_username: str = ''
    target_username: str = ''
    target_password: str = ''
    target_permission: str = ''

# Instantiate TestClient for FastAPI app
client = TestClient(app)

# Patch 'execute_user_action' and 'get_db_connection' to prevent real DB interactions
@patch("app.get_db_connection", return_value=MagicMock())
@patch("app.execute_user_action")
def test_manage_users_add_user(mock_execute, mock_get_db_connection):
    # Prepare the request payload
    request_payload = {
        "action": "add",
        "target_username": "new_user",
        "target_password": "new_pass",
        "target_permission": "Admin"
    }

    # Send POST request to the manage_users endpoint
    response = client.post("/admin/manage_users", json=request_payload)

    # Verify the response
    assert response.status_code == 200
    assert response.json() == {"message": "Action 'add' completed successfully."}

    # Verify 'execute_user_action' was called correctly
    mock_execute.assert_called_once_with("add", "", "new_user", "new_pass", "Admin")

# Test Adding a New User
@patch("app.execute_user_action")
def test_add_user_success(mock_execute_action):
    user_data = {
        "action": "add",
        "target_username": "new_user",
        "target_password": "password123",
        "target_permission": "Admin"
    }
    response = client.post("/admin/manage_users", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Action 'add' completed successfully."}
    mock_execute_action.assert_called_once_with("add", "", "new_user", "password123", "Admin")

# Test for 'Modify' Action 
@patch("app.get_db_connection")
@patch("app.execute_user_action", side_effect=HTTPException(status_code=404, detail="User not found, cannot modify"))
def test_manage_users_user_not_found_error(mock_execute, mock_get_db_connection):
    request_payload = {
        "action": "modify",  # or "delete" for testing deletion
        "current_username": "nonexistent_user",
    }
    response = client.post("/admin/manage_users", json=request_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found, cannot modify"}

# Test Modifying an Existing User
    
@patch("app.execute_user_action")
def test_modify_existing_user_success(mock_execute_action):
    user_data = {
        "action": "modify",
        "current_username": "existing_user",
        "target_username": "modified_user",
        "target_password": "newpassword",
        "target_permission": "Superuser"
    }
    response = client.post("/admin/manage_users", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Action 'modify' completed successfully."}
    mock_execute_action.assert_called_once_with("modify", "existing_user", "modified_user", "newpassword", "Superuser")
   

# Test for 'Delete' Action
@patch("app.get_db_connection", return_value=MagicMock())
@patch("app.execute_user_action")
def test_manage_users_delete_user(mock_execute, mock_get_db_connection):
    request_payload = {
        "action": "delete",
        "current_username": "existing_user",
    }
    response = client.post("/admin/manage_users", json=request_payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Action 'delete' completed successfully."}
    mock_execute.assert_called_once_with("delete", "existing_user", "", "", "")

# Test Deleting an Existing User

@patch("app.execute_user_action")
def test_delete_existing_user_success(mock_execute_action):
    user_data = {
        "action": "delete",
        "current_username": "existing_user"
    }
    response = client.post("/admin/manage_users", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Action 'delete' completed successfully."}
    mock_execute_action.assert_called_once_with("delete", "existing_user", "", "", "")

# Test Deleting a Non-existent User   
@patch("app.execute_user_action", side_effect=HTTPException(status_code=404, detail="User not found, cannot delete"))
def test_delete_nonexistent_user_failure(mock_execute_action):
    user_data = {
        "action": "delete",
        "current_username": "nonexistent_user"
    }
    response = client.post("/admin/manage_users", json=user_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found, cannot delete"}
    mock_execute_action.assert_called_once_with("delete", "nonexistent_user", "", "", "")

# Test for User Not Found Error

@patch("app.get_db_connection")
@patch("app.execute_user_action", side_effect=HTTPException(status_code=404, detail="User not found, cannot modify"))
def test_manage_users_user_not_found_error(mock_execute, mock_get_db_connection):
    request_payload = {
        "action": "modify",  # or "delete" for testing deletion
        "current_username": "nonexistent_user",
    }
    response = client.post("/admin/manage_users", json=request_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found, cannot modify"}

# Test for Unexpected Error

@patch("app.get_db_connection")
@patch("app.execute_user_action", side_effect=Exception("Unexpected error"))
def test_manage_users_unexpected_error(mock_execute, mock_get_db_connection):
    request_payload = {
        "action": "add",  # This can be any valid action to simulate the error
        "target_username": "new_user",
        "target_password": "new_pass",
        "target_permission": "Admin"
    }
    response = client.post("/admin/manage_users", json=request_payload)
    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]

# Test for the get_data_ Endpoint
@patch("app.get_db_connection")
def test_get_data_success(mock_get_db_connection):
    # Setup mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Define the data you expect to be returned from the database
    expected_data = [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"}
    ]
    
    # Configure the mock cursor to return the expected data
    mock_cursor.fetchall.return_value = expected_data
    
    # Make a request to the endpoint
    response = client.get("/data_test")
    
    # Verify the response
    assert response.status_code == 200
    assert response.json() == expected_data
    
    # Verify the SQL query was executed correctly
    mock_cursor.execute.assert_called_once_with("SELECT * FROM dataset Limit 3;")

# Define a Pydantic model for the expected request body
class QueryData(BaseModel):
    query: str

# Tests for the /data Endpoint  

@patch("app.get_db_connection")
def test_execute_valid_query_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test Item"}]

    query_data = {"query": "SELECT * FROM test_table"}
    response = client.post("/data", json=query_data)
    
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Test Item"}]
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")

def test_execute_empty_query_failure():
    query_data = {"query": ""}
    response = client.post("/data", json=query_data)
    
    assert response.status_code == 400
    assert response.json() == {"error": "No query provided"}


@patch("app.get_db_connection")
def test_execute_query_exception_handling(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    query_data = {"query": "SELECT * FROM test_table"}
    response = client.post("/data", json=query_data)
    
    assert response.status_code == 500
    assert response.json() == {"error": "Failed to execute query", "details": "Database error"}

