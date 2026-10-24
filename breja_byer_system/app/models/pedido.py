from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nome = Column(String, nullable=False)
    cliente_telefone = Column(String, nullable=True)  # WhatsApp / Telefone do cliente
    itens_resumo = Column(String, nullable=False)
    valor_total = Column(Float, nullable=False)
    status = Column(String, default="Pendente")  # Pendente, Separando, Pronto, Concluido
    data_criacao = Column(DateTime, default=datetime.utcnow)