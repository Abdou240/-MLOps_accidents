virtualenv env_mlflow
source env_mlflow/bin/activate
pip3 install mlflow
mlflow models build-docker --name general_model_server