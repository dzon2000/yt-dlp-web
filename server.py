import os
import threading
import time
from typing import Any

from flask import Flask, Response, jsonify, render_template, request, send_from_directory
from yt_dlp import YoutubeDL

app = Flask(__name__)
progress_lock = threading.Lock()
progress_info: dict[str, Any] = {"progress": 0.0, "file_name": None, "error": None}


def reset_progress() -> None:
    with progress_lock:
        progress_info["progress"] = 0.0
        progress_info["file_name"] = None
        progress_info["error"] = None


def report_progress(progress: dict[str, Any]) -> None:
    total_bytes = progress.get("total_bytes") or progress.get("total_bytes_estimate")
    if total_bytes:
        downloaded_bytes = progress.get("downloaded_bytes", 0) or 0
        percentage = min(max((downloaded_bytes / total_bytes) * 100, 0.0), 100.0)
        with progress_lock:
            progress_info["progress"] = percentage


def download_with_ytdlp(url: str) -> None:
    ydl_opts = {
        "outtmpl": "yolo_%(id)s.%(ext)s",
        "writethumbnail": False,
        "progress_hooks": [report_progress],
    }
    if "youtube" in url:
        ydl_opts["format_sort"] = ["res", "ext:mp4:m4a"]
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = os.path.basename(info.get("filepath") or ydl.prepare_filename(info))
            with progress_lock:
                progress_info["file_name"] = file_name
                progress_info["progress"] = 100.0
    except Exception as exc:  # noqa: BLE001 - surface in the UI instead of crashing the thread
        app.logger.exception("yt-dlp download failed for %s", url)
        with progress_lock:
            progress_info["error"] = str(exc)
            progress_info["progress"] = 100.0


@app.route("/progress")
def progress() -> Response:
    def generate():
        while True:
            with progress_lock:
                file_name = progress_info.get("file_name")
                error = progress_info.get("error")
                current_progress = progress_info.get("progress", 0.0)

            if file_name:
                yield f"data:{file_name}\n\n"
                return
            if error:
                yield f"data:ERROR:{error}\n\n"
                return
            yield f"data:{current_progress}\n\n"
            time.sleep(0.5)

    return Response(generate(), content_type="text/event-stream")


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/initiate", methods=["POST"])
def initiate():
    url = request.form.get("videoURL", "").strip()
    if not url:
        return jsonify({"status": "error", "message": "Missing video URL."}), 400

    reset_progress()
    thread = threading.Thread(target=download_with_ytdlp, args=(url,), daemon=True)
    thread.start()
    return jsonify({"status": "Download started"})


@app.route("/download/<file_name>")
def download(file_name):
    safe_name = os.path.basename(file_name)
    response = send_from_directory(".", safe_name)
    response.headers["Content-Disposition"] = "attachment"
    return response
