FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y && apt-get clean
RUN apt-get install -y curl python3.7 python3.7-dev python3.7-distutils
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py
RUN pip3 install joblib requests==2.21.0 fastapi uvicorn==0.17.0
ADD main.py /my_api/api.py
ADD unique_loc.csv /my_api/unique_loc.csv
WORKDIR /my_api/
ENV LC_CTYPE=UTF-8 LC_ALL=C.UTF-8 LANG=C.UTF-8
EXPOSE 8090
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8090"]