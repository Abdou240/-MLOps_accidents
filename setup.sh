docker rm $(docker ps -aq)
#docker system prune
docker image build ./docker-compose/API -t project_api:latest
docker image build ./docker-compose/streamlit -t project_streamlit:latest
docker image build ./docker-compose/mlflow -t mlflow_server:latest 
docker image build ./docker-compose/Database_Docker -t database_api:latest
docker-compose -f docker-compose/docker-compose.yml up --remove-orphans
#docker compose up