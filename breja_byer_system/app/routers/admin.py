import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.produto import Produto
from app.models.pedido import Pedido
from app.models.caderninho import Caderninho

router = APIRouter(prefix="/admin", tags=["Admin"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def verificar_auth(request: Request):
    return request.cookies.get("admin_logged_in") == "true"


def obter_pendentes_count(db: Session) -> int:
    try:
        pedidos = db.query(Pedido).all()
        pendentes = 0
        for p in pedidos:
            st = str(getattr(p, "status", "Pendente")).strip().title()
            if "Preparo" not in st and "Pronto" not in st and "Entregue" not in st and "Concluido" not in st:
                pendentes += 1
        return pendentes
    except Exception:
        return 0


def baixar_estoque_por_resumo(db: Session, itens_resumo: str):
    if not itens_resumo:
        return
    partes = itens_resumo.split(",")
    for parte in partes:
        parte = parte.strip()
        if "x" in parte:
            try:
                qtd_str, nome_prod = parte.split("x", 1)
                qtd = int(qtd_str.strip())
                nome_prod = nome_prod.strip()
                produto = db.query(Produto).filter(Produto.nome.ilike(nome_prod)).first()
                if produto:
                    produto.quantidade = max(0, produto.quantidade - qtd)
            except Exception as e:
                print(f"Erro ao baixar estoque do item {parte}: {e}")


@router.get("/estoque")
def admin_estoque(request: Request, busca: str = None, categoria: str = None, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        query = db.query(Produto)
        if busca:
            query = query.filter(Produto.nome.ilike(f"%{busca}%"))
        if categoria and categoria != "Todas":
            query = query.filter(Produto.categoria == categoria)
        produtos = query.all()
        categorias_db = db.query(Produto.categoria).distinct().all()
        lista_categorias = [c[0] for c in categorias_db if c[0]]
    except Exception:
        produtos = []
        lista_categorias = []

    pendentes_count = obter_pendentes_count(db)

    return templates.TemplateResponse(request, "admin/estoque.html", {
        "produtos": produtos, "busca": busca or "",
        "categoria_selecionada": categoria or "Todas", "categorias": lista_categorias,
        "pendentes_count": pendentes_count
    })


@router.post("/estoque/cadastrar")
def cadastrar_produto(
        request: Request, nome: str = Form(...), categoria: str = Form("Geral"),
        preco_custo: float = Form(0.0), preco_venda: float = Form(...),
        quantidade: int = Form(...), imagem: str = Form(None), db: Session = Depends(get_db)
):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        novo = Produto(nome=nome, categoria=categoria, preco_custo=preco_custo, preco_venda=preco_venda,
                       quantidade=quantidade, imagem=imagem)
        db.add(novo)
        db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/estoque", status_code=303)


@router.post("/estoque/excluir/{produto_id}")
def excluir_produto(produto_id: int, request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        prod = db.query(Produto).filter(Produto.id == produto_id).first()
        if prod:
            db.delete(prod)
            db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/estoque", status_code=303)


@router.post("/estoque/editar/{produto_id}")
def editar_produto(
        produto_id: int,
        request: Request,
        nome: str = Form(...),
        categoria: str = Form(...),
        preco_custo: float = Form(0.0),
        preco_venda: float = Form(...),
        quantidade: int = Form(...),
        db: Session = Depends(get_db)
):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if produto:
            produto.nome = nome
            produto.categoria = categoria
            produto.preco_custo = preco_custo
            produto.preco_venda = preco_venda
            produto.quantidade = quantidade
            db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/estoque", status_code=303)


@router.get("/kanban")
def admin_kanban(request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        hoje = datetime.now().date()
        pedidos = db.query(Pedido).all()
        pedidos_hoje = [p for p in pedidos if p.data_criacao and p.data_criacao.date() == hoje]
        if not pedidos_hoje:
            pedidos_hoje = pedidos
    except Exception:
        pedidos_hoje = []

    kanban = {"Pendente": [], "Em Preparo": [], "Pronto": [], "Entregue": []}
    for p in pedidos_hoje:
        st = str(getattr(p, "status", "Pendente")).strip().title()
        if "Preparo" in st:
            kanban["Em Preparo"].append(p)
        elif "Pronto" in st:
            kanban["Pronto"].append(p)
        elif "Entregue" in st or "Concluido" in st:
            kanban["Entregue"].append(p)
        else:
            kanban["Pendente"].append(p)

    pendentes_count = len(kanban["Pendente"])

    return templates.TemplateResponse(request, "admin/kanban.html", {
        "pedidos": pedidos_hoje,
        "kanban": kanban,
        "pendentes_count": pendentes_count
    })


@router.post("/kanban/mudar-status/{pedido_id}")
def mudar_status_pedido(pedido_id: int, request: Request, novo_status: str = Form(...), db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        p = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if p:
            p.status = novo_status
            db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/kanban", status_code=303)


@router.post("/kanban/excluir/{pedido_id}")
def excluir_pedido_kanban(pedido_id: int, request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        p = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if p:
            db.delete(p)
            db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/kanban", status_code=303)


@router.get("/pdv")
def admin_pdv(request: Request, erro: str = None, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        produtos = db.query(Produto).all()
    except Exception:
        produtos = []

    pendentes_count = obter_pendentes_count(db)

    return templates.TemplateResponse(request, "admin/pdv.html", {
        "produtos": produtos,
        "pendentes_count": pendentes_count,
        "erro": erro
    })


@router.get("/caixa")
def admin_caixa(request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/admin/pdv", status_code=303)


@router.post("/pdv/finalizar")
def pdv_finalizar(
        request: Request,
        cliente_nome: str = Form("Cliente Balcão"),
        itens_resumo: str = Form(...),
        valor_total: float = Form(...),
        forma_pagamento: str = Form("À Vista"),
        data_vencimento: str = Form(None),
        db: Session = Depends(get_db)
):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        if forma_pagamento == "Fiado":
            hoje = datetime.now()
            dividas_vencidas = db.query(Caderninho).filter(
                Caderninho.cliente_nome.ilike(cliente_nome),
                Caderninho.status == "Pendente",
                Caderninho.data_vencimento < hoje
            ).all()

            if dividas_vencidas:
                return RedirectResponse(url="/admin/pdv?erro=cliente_bloqueado", status_code=303)

        novo = Pedido(cliente_nome=cliente_nome, itens_resumo=itens_resumo, valor_total=valor_total, status="Entregue")
        db.add(novo)

        if forma_pagamento == "Fiado" and data_vencimento:
            dt_venc = datetime.strptime(data_vencimento, "%Y-%m-%d")
            novo_fiado = Caderninho(
                cliente_nome=cliente_nome,
                itens_resumo=itens_resumo,
                valor_total=valor_total,
                data_vencimento=dt_venc,
                status="Pendente"
            )
            db.add(novo_fiado)

        baixar_estoque_por_resumo(db, itens_resumo)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Erro ao finalizar PDV: {e}")
    return RedirectResponse(url="/admin/pdv", status_code=303)


@router.get("/caderninho")
def admin_caderninho(request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        dividas = db.query(Caderninho).order_by(Caderninho.data_vencimento.asc()).all()
    except Exception:
        dividas = []

    pendentes_count = obter_pendentes_count(db)

    return templates.TemplateResponse(request, "admin/caderninho.html", {
        "dividas": dividas,
        "pendentes_count": pendentes_count
    })


@router.post("/caderninho/pagar/{fiado_id}")
def pagar_fiado(fiado_id: int, request: Request, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        fiado = db.query(Caderninho).filter(Caderninho.id == fiado_id).first()
        if fiado:
            fiado.status = "Pago"
            db.commit()
    except Exception:
        db.rollback()
    return RedirectResponse(url="/admin/caderninho", status_code=303)


@router.get("/financeiro")
def admin_financeiro(request: Request, data_inicio: str = None, data_fim: str = None, db: Session = Depends(get_db)):
    if not verificar_auth(request):
        return RedirectResponse(url="/login", status_code=303)
    try:
        query = db.query(Pedido)
        if data_inicio:
            query = query.filter(Pedido.data_criacao >= datetime.strptime(data_inicio, "%Y-%m-%d"))
        if data_fim:
            query = query.filter(Pedido.data_criacao <= datetime.strptime(data_fim, "%Y-%m-%d"))
        pedidos_brutos = query.all()
    except Exception:
        pedidos_brutos = []

    # Identificar quais nomes/itens estão pendentes no caderninho para excluí-los do faturamento do DRE
    try:
        caderninhos_pendentes = db.query(Caderninho).filter(Caderninho.status == "Pendente").all()
        fiados_pendentes_valores = [(c.cliente_nome.strip().lower(), float(c.valor_total)) for c in
                                    caderninhos_pendentes]

        # Calcular o total geral que está pendente no caderninho (para exibir no card isolado)
        total_a_receber = sum(float(c.valor_total) for c in caderninhos_pendentes if c and c.valor_total is not None)
    except Exception:
        fiados_pendentes_valores = []
        total_a_receber = 0.0

    pedidos_Validos = []
    for p in pedidos_brutos:
        if not p or p.valor_total is None:
            continue
        c_nome = (p.cliente_nome or "").strip().lower()
        c_val = float(p.valor_total)

        is_fiado_pendente = any(fp[0] == c_nome and abs(fp[1] - c_val) < 0.01 for fp in fiados_pendentes_valores)

        if not is_fiado_pendente:
            pedidos_Validos.append(p)

    faturamento_total = sum(float(p.valor_total) for p in pedidos_Validos)
    custo_total = faturamento_total * 0.4
    lucro_estimado = faturamento_total - custo_total
    ticket_medio = faturamento_total / len(pedidos_Validos) if len(pedidos_Validos) > 0 else 0.0

    pendentes_count = obter_pendentes_count(db)

    return templates.TemplateResponse(request, "admin/financeiro.html", {
        "pedidos": pedidos_Validos,
        "faturamento_total": faturamento_total,
        "custo_total": custo_total,
        "lucro_estimado": lucro_estimado,
        "ticket_medio": ticket_medio,
        "total_a_receber": total_a_receber,  # <--- Enviado de forma isolada para o template
        "data_inicio": data_inicio or "", "data_fim": data_fim or "",
        "chart_dias_labels": [], "chart_dias_valores": [],
        "chart_cat_labels": ["Bebidas / Aluguer", "Outros"], "chart_cat_valores": [faturamento_total, 0.0],