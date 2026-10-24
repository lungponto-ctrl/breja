import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.produto import Produto
from app.models.pedido import Pedido
from app.routers.admin import baixar_estoque_por_resumo

router = APIRouter(tags=["Site"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/")
def index(request: Request, busca: str = None, categoria: str = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Produto)
        if busca:
            query = query.filter(Produto.nome.ilike(f"%{busca}%"))
        if categoria and categoria != "Todas":
            query = query.filter(Produto.categoria == categoria)

        produtos = query.all()
        categorias_db = db.query(Produto.categoria).distinct().all()
        lista_categorias = [c[0] for c in categorias_db if c[0]]
    except Exception as e:
        print(f"Erro ao carregar vitrine: {e}")
        produtos = []
        lista_categorias = []

    return templates.TemplateResponse(request, "site/index.html", {
        "produtos": produtos,
        "busca": busca or "",
        "categoria_selecionada": categoria or "Todas",
        "categorias": lista_categorias
    })


@router.post("/fazer-pedido")
def fazer_pedido(
        request: Request,
        cliente_nome: str = Form(...),
        cliente_telefone: str = Form(...),
        cliente_endereco: str = Form(...),
        itens_resumo: str = Form(...),
        valor_total: float = Form(...),
        db: Session = Depends(get_db)
):
    try:
        # Junta o endereço ao nome ou guarda formatado para o operador ver no Kanban
        info_completa = f"{cliente_nome} | Tel: {cliente_telefone} | End: {cliente_endereco}"

        novo = Pedido(
            cliente_nome=info_completa,
            cliente_telefone=cliente_telefone,
            itens_resumo=itens_resumo,
            valor_total=valor_total,
            status="Pendente"
        )
        db.add(novo)
        baixar_estoque_por_resumo(db, itens_resumo)
        db.commit()
    except Exception as e:
        print(f"Erro ao registar pedido: {e}")
        db.rollback()

    return RedirectResponse(url="/?sucesso=true", status_code=303)