from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    categoria = Column(String, index=True, default="Geral")
    preco_custo = Column(Float, default=0.0)
    preco_venda = Column(Float, default=0.0)
    quantidade = Column(Integer, default=0)
    imagem = Column(String, nullable=True)