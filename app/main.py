from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(
    title="Website Backend",
    description="API backend pour l'application ebook",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}