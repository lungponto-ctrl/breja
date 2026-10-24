from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    cargo = Column(String, default="atendente")  # 'admin' ou 'atendente'
    ativo = Column(Boolean, default=True)