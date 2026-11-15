# K. Vignesh Portfolio (Flask)

## Run it
1. Install Python 3.9+ from python.org
2. In this folder: `pip install -r requirements.txt`
3. Start the server: `python app.py`
4. Open http://127.0.0.1:5000

Note: opening `index.html` directly from the file manager shows the design and photos, but the visitor counter and contact form only work through `python app.py`.

## Python backend features (app.py)
- **Visitor counter** (`GET /api/visit`): counts each browser once per day and stores the total in SQLite.
- **Contact form**: `POST /api/contact` validates name, email and message, then saves them to SQLite (`portfolio.db`).
- **Read messages**: open `/admin/messages?key=YOUR_KEY`. Set your own key first:
  - Windows: `set ADMIN_KEY=mysecret`
  - Mac/Linux: `export ADMIN_KEY=mysecret`
