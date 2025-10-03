from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    vendas = relationship('Venda', back_populates='usuario')

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    categoria = Column(String)
    preco = Column(Float)
    vendas = relationship('Venda', back_populates='produto')

class Venda(Base):
    __tablename__ = 'vendas'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    quantidade = Column(Integer)
    valor_total = Column(Float)
    produto = relationship('Produto', back_populates='vendas')
    usuario = relationship('Usuario', back_populates='vendas')

class Forecast(Base):
    __tablename__ = 'forecast'
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    data_prevista = Column(Date)
    qtd_prevista = Column(Float)  # Agora representa RECEITA prevista
    intervalo_conf = Column(String)
    produto = relationship('Produto')
