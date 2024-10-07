import threading
import time
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, send_from_directory, Response, jsonify

app = Flask(__name__)
progress_info = {"progress": 0}
progress_lock = threading.Lock()


def report_progress(progress):
    total_bytes = progress['total_bytes']
    downloaded_bytes = progress.get('downloaded_bytes', 1)
    percentage = (downloaded_bytes / total_bytes) * 100
    with progress_lock:
        progress_info["progress"] = percentage


def download_with_ytdlp(url):
    ydl_opts = {
        # this is where you can edit how you'd like the filenames to be formatted
        "outtmpl": 'yolo_%(id)s.%(ext)s',
        "progress_hooks": [report_progress]
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_name = ydl.prepare_filename(info)
        with progress_lock:
            progress_info["file_name"] = file_name


@app.route('/progress')
def progress():
    def generate():
        while True:
            with progress_lock:
                progress = progress_info["progress"]

                yield f"data:{progress}\n\n"
                if "file_name" in progress_info:
                    yield f"data:{progress_info['file_name']}\n\n"
                    break
            time.sleep(0.5)
    return Response(generate(), content_type='text/event-stream')


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/initiate", methods=["POST"])
def initiate():
    with progress_lock:
        progress_info["progress"] = 0
    url = request.form["videoURL"]

    thread = threading.Thread(target=download_with_ytdlp, args=[url])
    thread.start()
    return jsonify({"status": "Download started"})


@app.route("/download/<file_name>")
def download(file_name):
    response = send_from_directory(".", file_name)
    response.headers['Content-Disposition'] = 'attachment'
    return response
