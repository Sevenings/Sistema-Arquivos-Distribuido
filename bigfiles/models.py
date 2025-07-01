from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from bigfiles.database import Base


# Relação N x M entre Máquinas e Shards
contem_table = Table(
    'contem', Base.metadata,
    Column(
        'id_maquina',
        ForeignKey('maquinas.id', ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        'id_shard',
        ForeignKey('shards.id', ondelete="CASCADE"),
        primary_key=True
    )
)


class Maquina(Base):
    __tablename__ = 'maquinas'

    id = Column(Integer, primary_key=True)
    endereco = Column(String(256), unique=True)
    ultimo_heartbeat = Column(DateTime, nullable=True)
    espaco_livre = Column(Integer, nullable=True) # Em Megabytes
    cpu = Column(Integer, nullable=True) # Em porcentagem

    shards = relationship('Shard', secondary=contem_table, back_populates='maquinas')

    def __repr__(self) -> str:
        return f"<Maquina {self.endereco}>"

    def viva(self):
        if self.ultimo_heartbeat is None:
            return False
        
        tempo_heartbeat = 60  # segundos - tempo padrão de heartbeat
        if datetime.now() - self.ultimo_heartbeat > timedelta(seconds=tempo_heartbeat):
            return False
        return True


class Shard(Base):
    __tablename__ = "shards"

    id = Column(Integer, primary_key=True)
    hash = Column(String(256))
    ordem = Column(Integer)
    id_arquivo = Column(Integer, ForeignKey('arquivos.id'))

    arquivo = relationship('Arquivo', back_populates='shards')
    maquinas = relationship(
        'Maquina',
        secondary=contem_table,
        back_populates='shards'
    )


class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(Integer, primary_key=True)
    hash = Column(String(256))
    nome = Column(String(256), unique=True)
    tamanho = Column(Integer)

    shards = relationship(
        'Shard',
        back_populates='arquivo',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

