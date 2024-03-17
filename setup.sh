docker rm $(docker ps -aq)
#docker system prune -a
# API
docker image build ./docker-compose/API -t project_api:latest
# Streamlit app
docker image build ./docker-compose/streamlit -t project_streamlit:latest
# MLflow server
docker image build -f ./docker-compose/mlflow/Dockerfile.mlflow_server ./docker-compose/mlflow -t mlflow_server:latest 
# Model api
docker image build -f ./docker-compose/mlflow/Dockerfile.model_api ./docker-compose/mlflow -t model_api:latest 
# DB api
docker image build ./docker-compose/Database_Docker -t database_api:latest

# Docker orquestration
docker-compose -f docker-compose/docker-compose.yml up --remove-orphans