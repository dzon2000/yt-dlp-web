from yt_dlp import YoutubeDL
from flask import Flask, redirect, render_template, request, send_from_directory

app = Flask(__name__)


def download_with_ytdlp(URLs):
    ydl_opts = {
        # this is where you can edit how you'd like the filenames to be formatted
        "outtmpl": './static/yolo.%(ext)s'
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(URLs)


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/initiate", methods=["POST"])
def initiate():
    url = request.form["videoURL"]
    download_with_ytdlp([url])
    return redirect("/download")


@app.route("/download")
def download():
    response = send_from_directory("./static/", "yolo.mp4")
    response.headers['Content-Disposition'] = 'attachment'
    return response


if __name__ == "__main__":
    URLS = ['https://x.com/Bairdric1/status/1764300268747800730?s=20']

    download(URLS)
