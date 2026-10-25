from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class Caderninho(Base):
    __tablename__ = "caderninho"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nome = Column(String, index=True)
    itens_resumo = Column(String)
    valor_total = Column(Float)
    data_compra = Column(DateTime, default=datetime.now)
    data_vencimento = Column(DateTime)
    status = Column(String, default="Pendente") # Pendente ou Pago