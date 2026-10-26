import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importa a engine, a Base e todos os modelos reais e válidos (incluindo o caderninho!)
from app.database import engine, Base
from app.models import produto, pedido, usuario, caderninho

# Cria automaticamente todas as tabelas se não existirem
Base.metadata.create_all(bind=engine)

# 1. Inicialização do FastAPI
app = FastAPI()

# Monta a pasta estática para o url_for('static', ...) funcionar perfeitamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configuração segura do caminho absoluto dos templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 2. Inclusão de todos os routers do sistema
from app.routers import admin, auth, site

app.include_router(site.router)
app.include_router(auth.router)
app.include_router(admin.router)