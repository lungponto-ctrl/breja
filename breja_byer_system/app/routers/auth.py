import os
from fastapi import APIRouter, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()

# Configuração segura do caminho absoluto dos templates para o router de autenticação
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Como estamos dentro de app/routers, subimos um nível para chegar a app/templates
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Palavra-passe de acesso ao painel admin
ADMIN_PASSWORD_CORRETA = "admin123"


@router.get("/login")
def pagina_login(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {"erro": None})


@router.post("/login")
def login_admin(request: Request, username: str = Form(...), password: str = Form(...)):
    # Credenciais atualizadas da Distribuidora do Merreis
    if username == "merreis" and password == "merreis6876":
        response = RedirectResponse(url="/admin/kanban", status_code=303)
        response.set_cookie(key="admin_logged_in", value="true")
        return response

    # Se errar a senha, recarrega com erro ou volta pro login
    return RedirectResponse(url="/login?erro=1", status_code=303)

@router.get("/logout")
def realizar_logout():
    res = RedirectResponse(url="/login", status_code=303)
    res.delete_cookie(key="admin_logged_in")
    return res