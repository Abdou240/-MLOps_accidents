FROM python:3.7-slim-buster
#FROM ubuntu:18.04
COPY model_requirements.txt /model_server/src/requirements.txt
WORKDIR /model_server/src
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
ADD . .
EXPOSE 5000
CMD mlflow models serve -m 'runs:/a98bbbd5944749cb86a4bd234a57ae60/rf_car_accidents' --no-conda