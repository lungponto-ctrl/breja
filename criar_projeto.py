import os
from pathlib import Path

# Definição da estrutura de pastas e arquivos do sistema Breja Byer
structure = {
    "breja_byer_system": [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/models/__init__.py",
        "app/models/produto.py",
        "app/models/pedido.py",
        "app/models/caixa.py",
        "app/models/usuario.py",
        "app/routers/__init__.py",
        "app/routers/site.py",  # Rotas da Loja Virtual (Cliente)
        "app/routers/admin.py",  # Rotas do Painel Administrativo / PDV
        "app/routers/auth.py",  # Autenticação e Login
        "app/services/__init__.py",
        "app/services/estoque.py",  # Regras de conversão de fardo/unidade e baixa
        "app/services/caixa.py",  # Regras de abertura, fechamento e sangria
        "app/static/css/style.css",
        "app/static/js/main.js",
        "app/static/img/.gitkeep",
        "app/templates/site/index.html",  # Vitrine
        "app/templates/site/carrinho.html",  # Carrinho e Checkout
        "app/templates/site/status.html",  # Acompanhar pedido
        "app/templates/admin/kanban.html",  # Monitor de pedidos em tempo real
        "app/templates/admin/pdv.html",  # Frente de caixa balcão
        "app/templates/admin/estoque.html",  # Gestão de produtos
        "app/templates/admin/caixa.html",  # Controle de caixa
        "tests/__init__.py",
        "tests/test_estoque.py",
        "tests/test_caixa.py",
        ".env.example",
        "requirements.txt",
        "README.md"
    ]
}


def create_project_structure(base_path, structure_dict):
    base = Path(base_path)

    for root, paths in structure_dict.items():
        root_path = base / root
        print(f"📁 Criando diretório raiz: {root_path}")

        for path_str in paths:
            full_path = root_path / path_str

            if path_str.endswith("/"):
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"   Criando pasta: {full_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)

                if not full_path.exists():
                    if full_path.name == ".env.example":
                        full_path.write_text(
                            "DATABASE_URL=sqlite:///breja_byer.db\nSECRET_KEY=sua_chave_secreta_aqui\n")
                    elif full_path.name == "requirements.txt":
                        full_path.write_text("fastapi\nuvicorn\nsqlalchemy\npydantic\njinja2\npython-dotenv\n")
                    else:
                        full_path.write_text("")
                    print(f"   📄 Criando arquivo: {full_path}")
                else:
                    print(f"   ⚠️ Arquivo já existe: {full_path}")


if __name__ == "__main__":
    print("🚀 Iniciando a criação da estrutura do sistema Breja Byer...")
    create_project_structure(".", structure)
    print("\n✨ Projeto estruturado com sucesso! Pronto para codar.")