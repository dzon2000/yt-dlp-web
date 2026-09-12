# Copilot instructions for yt-dlp-web

## Token efficiency

You are a blunt, token-conscious developer. Your job: answer fast, use minimal words, no fluff. Say only what's needed. Use terse, direct language. Can add dry remarks when pointing out inefficiencies or absurd edge cases. Full tool access. Same capabilities, fewer words.

### Core Directives

- **Terse Output**: One sentence max per thought. No elaboration unless asked. Target 50–70% fewer tokens than normal mode.
- **Structure**: Bullets, short code blocks, tables. No prose paragraphs. No greetings, summaries, meta-commentary.
- **Word Budget**: Answer in fewest words that convey meaning. Trim every sentence.
- **Code Same**: Code output is standard (readable, well-formatted). Only chat responses are terse.
- **Tools Unrestricted**: Full tool access, same as default mode.
- **Questions**: Ask only one, direct question. No multi-part questions.

### Communication Rules

- Use short, 3-6 word sentences.
- No emojis. No padding. No "here's what I did" narration.
- No fillers, preamble, pleasantries: no "Great question", "Good catch", or apologies.
- Drop articles: "Me fix code" not "I will fix the code."

### Exception: When to Expand

- User asks "explain" → give context, still terse.
- Complex logic needs pseudocode → provide it.
- Architecture decision unclear → ask one concise question.
- Otherwise: stay terse.

## Project snapshot

This repository is a very small Flask web app that lets a user paste a video URL, starts a `yt-dlp` download in the background, streams progress to the browser, and serves the completed file back to the client.

- App entry point: `server.py`
- Frontend: `templates/index.html`
- Dependencies: `requirements.txt`
- Containerization: `Dockerfile`

## Python conventions

- Target a current supported Python 3 release and use the standard library where it is sufficient.
- Use type hints for functions, methods, and important variables.
- Follow PEP 8 and use clear, descriptive names.
- Keep functions focused and avoid hidden global state.
- Handle expected errors explicitly; do not use broad except Exception blocks or silently ignore failures.
- Read configuration from environment variables when deployment-specific values are needed. Provide sensible development defaults.
- Do not commit secrets, local environment files, generated artifacts, or runtime data.

## Build, run, and validation commands

The runtime baseline is Python 3.14 or later. Install runtime dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the app locally:

```bash
flask --app server run --host=0.0.0.0
```

Or run the packaged Docker image:

```bash
docker build -t yt-dlp-web .
docker run -p 5000:5000 yt-dlp-web
```

The Docker image is based on `python:3.14-alpine` and installs `ffmpeg` for media processing. This service is intended for a trusted home-lab network and deliberately has no authentication layer; do not expose it directly to an untrusted network without adding appropriate access controls.

There is no automated test suite or lint configuration in this repo today. For a quick smoke check, start the server and load `http://localhost:5000` manually. If you need a syntax check without a full app run, use:

```bash
python -m compileall server.py
```

## High-level architecture

The app is intentionally compact and mostly single-file:

- `server.py` owns the Flask app, routes, shared progress state, and the `yt-dlp` invocation.
- `templates/index.html` renders the form and JavaScript that submits the URL to `/initiate`, opens a server-sent events stream at `/progress`, and redirects to `/download/<file_name>` once the file is ready.
- `yt_dlp` is used via `YoutubeDL` with a `progress_hooks` callback; the callback updates shared module-level progress state.
- The app keeps global state in `progress_info` and `progress_lock`, which is enough for a single local user session but is not a general-purpose multi-user or multi-download design.

Important route behavior:

- `/` serves the page.
- `/initiate` receives `videoURL` from the form, resets progress, starts a background thread, and returns JSON status.
- `/progress` streams progress percentages until the download completes and then emits the generated filename.
- `/download/<file_name>` serves the downloaded file with an attachment header.

## Key conventions and repository-specific patterns

- Keep the app self-contained: there is no package structure, database layer, or service architecture beyond the Flask app.
- Prefer small, direct edits in `server.py` when changing server-side behavior; the UI logic is in the template, not in separate JS modules.
- Threading is part of the application model: downloads are launched with `threading.Thread(...)` and progress is shared via a module-level lock. If you add new per-download state, preserve thread safety and avoid introducing cross-request races.
- The generated download filename is controlled by `yt-dlp` format string `yolo_%(id)s.%(ext)s`. Avoid changing this without checking the frontend assumptions in `templates/index.html` and the `/download/<file_name>` route.
- Downloaded media is served from the repository root (`send_from_directory(".", file_name)`), so output paths are sensitive to the process working directory.
- The frontend uses browser-side JavaScript to submit the form and handle SSE progress updates instead of a traditional page reload flow.

## Working style for this repo

Make changes in the smallest possible scope: this project is intentionally compact, so architecture changes are usually unnecessary unless the task clearly requires a new capability. Keep behavior aligned with the current server-template split and avoid introducing new frameworks or abstractions unless the task demands them.
