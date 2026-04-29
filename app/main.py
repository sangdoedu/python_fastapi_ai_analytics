
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import upload, query

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(upload.router)
app.include_router(query.router)

@app.get("/")
async def home(request: Request):
    print('hello')
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/health')
async def health():
    return {'status': 'ok'}

ddd