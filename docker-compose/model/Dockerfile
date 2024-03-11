# FROM python:3.7-slim-buster
# #FROM ubuntu:18.04
# COPY model_requirements.txt /model_server/src/requirements.txt
# WORKDIR /model_server/src
# RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
# ADD . .
# EXPOSE 5000
# CMD mlflow models serve -m 'runs:/a98bbbd5944749cb86a4bd234a57ae60/rf_car_accidents' --no-conda


FROM python:3.8.10

ENV MLFLOW_HOME /opt/mlflow
ENV SERVER_PORT 8000
ENV SERVER_HOST 0.0.0.0
ENV FILE_STORE ${MLFLOW_HOME}/fileStore
ENV ARTIFACT_STORE ${MLFLOW_HOME}/artifactStore

RUN pip install mlflow 

# && \
#     mkdir -p ${MLFLOW_HOME}/scripts && \
#     mkdir -p ${FILE_STORE} && \
#     mkdir -p ${ARTIFACT_STORE}

#COPY src/mlflow/run.sh ${MLFLOW_HOME}/scripts/run.sh
#RUN chmod +x ${MLFLOW_HOME}/scripts/run.sh

EXPOSE ${SERVER_PORT}/tcp

#VOLUME ["${MLFLOW_HOME}/scripts/", "${FILE_STORE}", "${ARTIFACT_STORE}"]

ADD ./../../mlruns "${MLFLOW_HOME}/mlruns"

WORKDIR ${MLFLOW_HOME}

#ENTRYPOINT ["./scripts/run.sh"]

#CMD "mlflow server --file-store ${FILE_STORE} --default-artifact-root ${ARTIFACT_STORE} --host ${SERVER_HOST} --port ${SERVER_PORT}"
#RUN "mlflow server --host 0.0.0.0 --port 8080"