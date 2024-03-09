FROM python:3.10-bookworm

RUN pip3 install requests==2.21.0 streamlit pandas
ADD streamlit.py /ui/streamlit.py
ADD v_commune_2023.csv /ui/com.csv
WORKDIR /ui
ENV LC_CTYPE=UTF-8 LC_ALL=C.UTF-8 LANG=C.UTF-8
CMD streamlit run streamlit.py