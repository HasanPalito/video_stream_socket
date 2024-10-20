from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_html():
    # Open and read the HTML file
    html_file_path = Path("client.html")
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

uvicorn.run(app,port=9000,host="0.0.0.0")