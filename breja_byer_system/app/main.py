import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine, Base
from app.models import produto, pedido, usuario, caderninho

Base.metadata.create_all(bind=engine)

app = FastAPI()

# <--- ESTA LINHA É OBRIGATÓRIA PARA O url_for FUNCIONAR NO FASTAPI --->
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

from app.routers import admin, auth, site
app.include_router(site.router)
app.include_router(auth.router)
app.include_router(admin.router)