import os
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

# Importações da base de dados e dos modelos para que o SQLite crie as tabelas automaticamente
from app.database import engine, Base
from app.models import produto, pedido  # Garante que os modelos são carregados pelo SQLAlchemy

# Criação automática das tabelas no banco de dados se não existirem
Base.metadata.create_all(bind=engine)

# 1. Inicialização do FastAPI
app = FastAPI()

# Configuração segura do caminho absoluto dos templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 2. Inclusão de todos os routers do sistema (Vitrine/Site, Auth/Login e Admin/Painel)
from app.routers import admin, auth, site

app.include_router(site.router)
app.include_router(auth.router)
app.include_router(admin.router)