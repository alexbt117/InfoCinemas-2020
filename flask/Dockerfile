FROM ubuntu:16.04

RUN apt-get update \
    && apt-get -y upgrade \ 
    && apt-get -y install software-properties-common \
    && apt-get -y install python3-pip 

RUN pip3 install --upgrade pip

RUN mkdir /flask

COPY app /flask
COPY requirements.txt /flask/requirements.txt

RUN pip3 install -r /flask/requirements.txt

ENTRYPOINT ["python3", "-u","/flask/app.py"]