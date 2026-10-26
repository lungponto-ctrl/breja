import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine, Base
from app.models import produto, pedido, usuario, caderninho

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Caminho absoluto da pasta app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montagem explícita e segura da pasta static dentro de app/static
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"AVISO: A pasta static não foi encontrada em {static_dir}")

# Configuração dos templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

from app.routers import admin, auth, site
app.include_router(site.router)
app.include_router(auth.router)
app.include_router(admin.router)