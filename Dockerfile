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

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python3", "-c", "from urllib.request import urlopen; response = urlopen('http://127.0.0.1:5000/', timeout=4); assert response.status == 200"]

CMD [ "flask", "--app", "server",  "run", "--host=0.0.0.0" ]
