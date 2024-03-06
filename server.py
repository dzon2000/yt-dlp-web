from yt_dlp import YoutubeDL
from flask import Flask, redirect, render_template, request, send_from_directory

app = Flask(__name__)


def download_with_ytdlp(url):
    ydl_opts = {
        # this is where you can edit how you'd like the filenames to be formatted
        "outtmpl": 'yolo_%(id)s.%(ext)s'
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # ydl.download(URLs)
        return ydl.prepare_filename(info)


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/initiate", methods=["POST"])
def initiate():
    url = request.form["videoURL"]
    file_name = download_with_ytdlp(url)
    return redirect(f"/download/{file_name}")


@app.route("/download/<file_name>")
def download(file_name):
    response = send_from_directory(".", file_name)
    response.headers['Content-Disposition'] = 'attachment'
    return response


if __name__ == "__main__":
    URLS = ['https://x.com/Bairdric1/status/1764300268747800730?s=20']

    download(URLS)
