# Voice Shopping Assistant - Project

This project is a simple Voice Shopping Assistant prototype:
- Frontend: Plain HTML/CSS/JS (index.html)
- Backend: Flask API (app.py) using spaCy for NLP and FakeStore API as product catalog
- Features:
  - Use your microphone to speak product queries (search, add, remove)
  - Backend parses intent (add/remove/find), extracts item and quantity
  - Backend fetches products from https://fakestoreapi.in and returns suggestions
  - Shopping cart stored in backend memory (demo)

## Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Run backend:

```bash
python app.py
```

4. Open `index.html` in Chrome (use Live Server or a local static server) and click **Start Voice Command**.

## Notes
- This is a demo. The cart is stored in memory and will reset when the backend restarts.
- For production, use a database and a production WSGI server.
- Make sure to use Chrome/Edge for Web Speech API support.
