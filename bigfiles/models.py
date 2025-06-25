import os
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from bigfiles import config

engine = create_engine(config.get("DATABASE_PATH"))

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


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
    cpu = Column(Integer) # Em porcentagem

    shards = relationship('Shard', secondary=contem_table, back_populates='maquina')

    def __repr__(self) -> str:
        return f"<Maquina {self.endereco}>"


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


def iniciar_db():
    Base.metadata.create_all(engine)
