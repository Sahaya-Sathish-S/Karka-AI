# Karka AI website

A responsive Flask website for Karka AI (Nagercoil): looping hero video, automatic course showcase, course detail pages, learner stories, free career-call form, a white enrollment page backed by SQLite, a Google Maps location section and the Karka AI doubt assistant.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal inside the `Karka AI` folder.
3. (Optional) create a virtual environment: `python -m venv .venv` then activate it.
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open http://127.0.0.1:5000

For auto-reload while developing, run with `FLASK_DEBUG=1 python app.py`. Debug mode is OFF by default.
Before deployment set a real `SECRET_KEY` environment variable and run with a production WSGI server (for example `gunicorn app:app`).

## Karka AI location
The location section (id `contact`) sits above the footer on the home page; the footer, enrollment page and chatbot also link to it.
- `KARKA_MAPS_URL` (default: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw) is the button / link target.
- `KARKA_MAPS_EMBED_URL` is the inline map. Google does not allow short `maps.app.goo.gl` links inside an iframe, so by default it searches "Karka AI, Nagercoil". To pin the exact spot: open the location in Google Maps -> Share -> Embed a map -> copy the `src="..."` URL and set it as `KARKA_MAPS_EMBED_URL` (or paste it into `MAPS_EMBED_URL` in `app.py`).

## Project structure
- `app.py` - Flask routes, SQLite persistence, chatbot API
- `templates/` - HTML templates
- `style/main.css` - all styles (smoothness layer, white form page and location styles are at the end)
- `js/main.js` - hero slider and menu; `js/smooth.js` - scroll reveals, video/animation pausing; `js/chatbot.js` - assistant
- `images/`, `videos/` - media
- `instance/` - local SQLite database (created automatically)

See `README_CHATBOT.md` for the AI assistant / OpenRouter setup.
