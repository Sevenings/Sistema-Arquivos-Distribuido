import os
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

basedir = os.path.abspath(os.path.dirname(__file__))

Base = declarative_base()

class Maquina(Base):
    __tablename__ = 'maquinas'

    id = Column(Integer, primary_key=True)
    endereco = Column(String(256), unique=True)
    ultimo_heartbeat = Column(DateTime)
    espaco_livre = Column(Integer) # Em Megabytes

    shards = relationship('Shard', back_populates='maquina')


class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(Integer, primary_key=True)
    hash = Column(String(256))
    nome = Column(String(256), unique=True)
    tamanho = Column(Integer)

    shards = relationship('Shard', back_populates='arquivo')


class Shard(Base):
    __tablename__ = "shards"
    id = Column(Integer, primary_key=True)

    hash = Column(String(256))
    ordem_na_fila = Column(Integer)

    arquivo_id = Column(Integer, ForeignKey('arquivos.id'))
    maquina_id = Column(Integer, ForeignKey('maquinas.id'))

    arquivo = relationship('Arquivo', back_populates='shards')
    maquina = relationship('Maquina', back_populates='shards')



