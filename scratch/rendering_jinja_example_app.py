import os

# Lets use FastAPI
from fastapi import FastAPI, Depends, HTTPException
from fastapi import FastAPI
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

# pylint: disable=C0103
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "title": "FastAPI", "message": "Hello, FastAPI!"})

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000, log_level="info")

