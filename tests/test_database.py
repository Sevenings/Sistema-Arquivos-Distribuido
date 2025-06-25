import os, pytest
from sqlalchemy import create_engine
from bigfiles.models import Maquina, SessionLocal, iniciar_db
from datetime import datetime


def test_criar_db():
    iniciar_db()

    # m_a = Maquina(
    #         endereco="maquina_a",
    #         ultimo_heartbeat=datetime.now(),
    #         espaco_livre=250000,
    #         cpu=1
    #         )
   
    session = SessionLocal()

    # session.add(m_a)
    session.commit()

    maquinas = session.query(Maquina).all()
    print("Máquinas:")
    print(len(maquinas))

    session.close()



if __name__ == "__main__":
    test_criar_db()
