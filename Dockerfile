FROM python:3.12-alpine

LABEL author="cierpki"

WORKDIR /opt/downloader

COPY static/ ./static
COPY templates/ ./templates
COPY requirements.txt ./
COPY server.py ./

RUN pip install -r requirements.txt 

EXPOSE 5000

CMD [ "flask", "--app", "server",  "run", "--host=0.0.0.0" ]
