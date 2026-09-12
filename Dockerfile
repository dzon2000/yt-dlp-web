FROM python:3.14-alpine

LABEL author="cierpki"

WORKDIR /opt/downloader

COPY templates/ ./templates
COPY static/ ./static
COPY requirements.txt ./
COPY server.py ./

RUN apk add --no-cache ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "flask", "--app", "server",  "run", "--host=0.0.0.0" ]
