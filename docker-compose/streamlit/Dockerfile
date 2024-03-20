FROM python:3.10-bookworm

RUN pip3 install requests streamlit pandas --progress-bar off
ADD streamlit.py /ui/streamlit.py
ADD v_commune_2023.csv /ui/com.csv
ADD containers.png /ui/containers.png
ADD diagram.png /ui/diagram.png
WORKDIR /ui
ENV LC_CTYPE=UTF-8 LC_ALL=C.UTF-8 LANG=C.UTF-8
CMD streamlit run streamlit.py