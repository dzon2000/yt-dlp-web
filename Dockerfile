FROM python:3.12

LABEL author="cierpki"

WORKDIR /opt/downloader

COPY static/ ./
COPY templates/ ./
COPY requirements.txt ./
COPY server.py ./

RUN pip install -r requirements.txt 

EXPOSE 5000

CMD [ "flask", "--app", "server",  "run", "--host=0.0.0.0" ]
