from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from fastapi import FastAPI, HTTPException, Form
print()
app = FastAPI()

global_speed=0
global_degree = 0
global_current_speed = 0
global_current_degree = 0

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def get_html():
    # Open and read the HTML file
    html_file_path = Path("client_v1.html")
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/3d", response_class=HTMLResponse)
async def get_html():
    # Open and read the HTML file
    html_file_path = Path("3d_image.html")
    html_content = html_file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/{file}")
async def get_dynamic_file(file: str):
    file_path = Path(file)

    if file_path.exists():
        if file_path.suffix in ['.html']:
            return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
        elif file_path.suffix in ['.obj', '.mtl', '.jpg', '.png']:  # Add other binary types as needed
            return Response(content=file_path.read_bytes())
    
    raise HTTPException(status_code=404, detail="File not found")


    
uvicorn.run(app,port=9000,host="0.0.0.0")