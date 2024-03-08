FROM python:3.10-bookworm

RUN pip3 install requests==2.21.0 streamlit
ADD streamlit.py /ui/streamlit.py
WORKDIR /ui
ENV LC_CTYPE=UTF-8 LC_ALL=C.UTF-8 LANG=C.UTF-8
CMD streamlit run streamlit.py