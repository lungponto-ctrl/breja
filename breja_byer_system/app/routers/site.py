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
        cliente_endereco: str = Form("Retirada no Balcão"),
        itens_resumo: str = Form(...),
        valor_total: float = Form(...),
        forma_pagamento: str = Form("Pix"),          # <--- Novo campo recebido do carrinho
        precisa_troco: str = Form("Não"),            # <--- Novo campo (Sim/Não)
        troco_para: float = Form(0.0),               # <--- Novo campo com o valor do troco
        db: Session = Depends(get_db)
):
    try:
        # Formata a informação de pagamento e troco para aparecer organizada no painel/Kanban
        pagamento_info = f"Pagto: {forma_pagamento}"
        if forma_pagamento == "Dinheiro" and precisa_troco == "Sim" and troco_para > 0:
            pagamento_info += f" (Troco para R$ {troco_para:.2f})"

        # Junta todas as informações do cliente num único texto estruturado para o operador consultar facilmente
        info_completa = f"{cliente_nome} | Tel: {cliente_telefone} | End: {cliente_endereco} | {pagamento_info}"

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