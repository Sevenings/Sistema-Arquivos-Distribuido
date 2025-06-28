from Pyro5.api import expose, Daemon, locate_ns
from sqlalchemy import desc
from bigfiles.database import iniciar_db, session
from bigfiles.models import Maquina


@expose
class Master:
    def __init__(self):
        pass

    def start(self):
        # Iniciar o banco de dados
        iniciar_db()

        # Se registrar no serviço de nomes
        daemon = Daemon()
        ns = locate_ns()
        uri = daemon.register(self)
        ns.register("bigfs.master", uri)
        daemon.requestLoop()


    def registrar_nova_maquina(self):
        # Cria uma nóva máquina no banco de dados
        # Pega o id dessa última máquina criada
        # E retorna o id
        ultima_maquina = session.query(Maquina).order_by(desc(Maquina.id)).first()
        novo_id = ultima_maquina.id + 1 if ultima_maquina else 0
        nova_maquina = Maquina(id=novo_id, endereco=f"bigfs.node.{novo_id}")
        session.add(nova_maquina)
        session.commit()
        return novo_id



    def upload_fragmento(self, nome_arquivo: str, hash_arquivo: str, hash_fragmento: str, ordem: int, fragmento_data: bytes):
        """
        Função que recebe um fragmento, escolhe as melhores máquinas para guardá-lo, envia a elas
        e atualiza o index no banco de dados.

        :param nome_arquivo: nome do arquivo ao qual o fragmento pertence
        :param hash_arquivo: string hash que identifica o arquivo
        :param hash_fragmento: string hash que identifica os bytes do fragmento
        :param ordem: número que identifica qual a ordem do fragmento
        :param fragmento_data: dados do fragmento
        :return: resultado da operação
        """

        print("Upload de arquivo:")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Hash arquivo: {hash_arquivo}")
        print(f"Hash fragmento: {hash_fragmento}")
        print(f"Ordem: {ordem}")



    def listar_arquivos(self):
        pass


    def remover_arquivo(self, nome_arquivo: str):
        pass


    def baixar_arquivo(self, nome_arquivo):
        pass

