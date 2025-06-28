import pytest

from bigfiles.database import iniciar_db
from bigfiles.database import session
from bigfiles.models import Maquina
from datetime import datetime

def test_db():
    iniciar_db()

    maquina_old = session.query(Maquina).filter_by(endereco="node_1").first()
    if maquina_old:
        session.delete(maquina_old)
        session.commit()


    maquina_a = Maquina(
            endereco="node_1",
            ultimo_heartbeat=datetime.now(),
            espaco_livre=24000,
            cpu=5)

    session.add(maquina_a)
    session.commit()

    maquina_query = session.query(Maquina).filter_by(endereco="node_1").first()

    assert maquina_a.id == maquina_query.id
    assert maquina_a.ultimo_heartbeat == maquina_query.ultimo_heartbeat
    assert maquina_a.espaco_livre == maquina_query.espaco_livre
    assert maquina_a.cpu == maquina_query.cpu


