docker rm $(docker ps -aq)
#docker system prune
docker image build ./docker-compose/API -t project_api:latest
docker image build ./docker-compose -t project_streamlit:latest
docker build -f Dockerfile.mlfow_server . -t mlflow_server:latest 
docker-compose -f docker-compose/docker-compose.yml up --remove-orphans
#docker compose up