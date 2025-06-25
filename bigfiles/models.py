import os
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import declarative_base, relationship

basedir = os.path.abspath(os.path.dirname(__file__))

Base = declarative_base()


# Relação N x M entre Máquinas e Shards
contem_table = Table(
    'contem', Base.metadata,
    Column('id_maquina',   ForeignKey('maquinas.id'),   primary_key=True),
    Column('id_shard',  ForeignKey('shards.id'),  primary_key=True)
)


class Maquina(Base):
    __tablename__ = 'maquinas'

    id = Column(Integer, primary_key=True)
    endereco = Column(String(256), unique=True)
    ultimo_heartbeat = Column(DateTime)
    espaco_livre = Column(Integer) # Em Megabytes
    cpu = Column(Integer)

    shards = relationship('Shard', secondary=contem_table, back_populates='maquina')


class Shard(Base):
    __tablename__ = "shards"

    id = Column(Integer, primary_key=True)
    hash = Column(String(256))
    ordem = Column(Integer)
    id_arquivo = Column(Integer, ForeignKey('arquivos.id'))

    arquivo = relationship('Arquivo', back_populates='shards')
    maquina = relationship('Maquina', secondary=contem_table, back_populates='shards')


class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(Integer, primary_key=True)
    hash = Column(String(256))
    nome = Column(String(256), unique=True)
    tamanho = Column(Integer)

    shards = relationship('Shard', back_populates='arquivo')


