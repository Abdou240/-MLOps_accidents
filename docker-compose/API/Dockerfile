FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y && pip3 install uvicorn==0.24.0.post1
ADD main.py /my_api/api.py
WORKDIR /my_api/
EXPOSE 8000
CMD python3 api.py