from datetime import datetime
from Pyro5.api import expose, Daemon, locate_ns, Proxy
from Pyro5.errors import NamingError
import os
from pathlib import Path
import json
import time
import psutil
import threading

from config import config

from .hash import calcular_sha256_bytes
from .erros.erros import ErroArquivoJaExiste, ErroArquivoNaoExiste, ErroHashInvalido
import base64

from .index import Index
from .logs import registra_logs

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'




@expose
class Node:
    def __init__(self, address='localhost', port=8989, index_file='index.json', files_folder='files'):
        self.ADDR = address
        self.PORT = port
        self.INDEX_FILE = index_file
        self.FILES_FOLDER = files_folder
        self.client_ip = None
        self.ID_CACHE_PATH = "id.txt"
        self.id = self.loadId()


    def start(self):
        # Se não houver ID (Primeira vez iniciado) acessa o master e procura um ID
        if self.id is None:
            try: 
                self.cadastrar_no_cluster()
            except NamingError:
                registra_logs("NODE", "Master não encontrado")
                print("Master não encontrado.")
                return

        registra_logs("NODE", f"Iniciando node {self.id}")
        print(f"Iniciando node {self.id}")

        # Inicia o index.json
        self.setup()

        # Thread para os heartbeats
        self.heartbeat_thread = threading.Thread(target=self.heartbeat, daemon=True)
        self.heartbeat_thread.start()

        # Se inscreve no servidor de nomes e aguarda requisições
        daemon = Daemon()
        ns = locate_ns()
        uri = daemon.register(self)
        ns.register(f"bigfs.node.{self.id}", uri)
        registra_logs("NODE", f"Node {self.id} registrado no servidor de nomes")
        daemon.requestLoop()

    
    def loadId(self):
        print("Carregando ID")
        if not Path(self.ID_CACHE_PATH).exists():
            print("Arquivo ID não existe")
            return None
        print("Arquivo ID existe. Carregando ID")
        with open(self.ID_CACHE_PATH, "r") as f:
            id = int(f.read())
        print(f"ID é {id}")
        return id

    
    def saveId(self):
        with open(self.ID_CACHE_PATH, "w") as f:
            f.write(str(self.id))


    def cadastrar_no_cluster(self):
        print("Se cadastrando no cluster")
        with Proxy("PYRONAME:bigfs.master") as master:
            self.id = master.registrar_nova_maquina()
            self.saveId()


    def run(self):
        self.setup()


    def setup(self):
        self._criar_index()
        self._criar_diretorios_arquivos()


    def _criar_index(self):
        if not Path(self.INDEX_FILE).exists():
            # Cria o arquivo
            with open(self.INDEX_FILE, 'w') as file:
                file.write('{}')


    def _criar_diretorios_arquivos(self):
        path_files_folder = Path(FILES_FOLDER)
        if not path_files_folder.exists():
            path_files_folder.mkdir()


    def verificar_cp(self, nome_arquivo):
        with Index() as index:
            if index.existe(nome_arquivo):
                return False
        return True


    def upload_fragmento(self, nome_arquivo, arquivo_data_pkg, ordem, hash_esperado):
        nome_fragmento = f"{nome_arquivo}_{ordem}"
        registra_logs("NODE", f"Recebendo fragmento {nome_fragmento}")

        # Verifica se arquivo existe
        if not self.verificar_cp(nome_fragmento):
            registra_logs("ERRO", f"Fragmento {nome_fragmento} já existe")
            raise ErroArquivoJaExiste 

        # Debug: Printa que está recebendo o fragmento
        print(f"Recebido fragmento {nome_fragmento}")

        # Extrai os dados do arquivo
        encoding = arquivo_data_pkg.get('encoding')
        data = arquivo_data_pkg.get('data')
        if encoding == 'base64':
            data = base64.b64decode(data)

        # Calcular o Hash
        hash = calcular_sha256_bytes(data)

        if hash != hash_esperado:
            registra_logs("ERRO", f"Hash inválido para fragmento {nome_fragmento}")
            raise ErroHashInvalido

        # Salvar o fragmento
        with open(f"{FILES_FOLDER}/{nome_fragmento}", 'wb') as file:
            file.write(data)

        # Registrar no indice
        with Index() as index:
            index.adicionar(nome_fragmento, hash, ordem)
        
        registra_logs("NODE", f"Fragmento {nome_fragmento} salvo com sucesso")

    def verificar_rm(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return False
        return True


    def rm(self, nome_arquivo, ordem):
        # Verifica se arquivo existe
        if not self.verificar_rm(f"{nome_arquivo}_{ordem}"):
            raise ErroArquivoNaoExiste

        # Debug: Printa que está removendo o fragmento
        print(f"Removendo fragmento {nome_arquivo}_{ordem}")

        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo, ordem)

        # Apagar arquivo
        os.remove(path_arquivo)

        # Registrar no índice
        with Index() as index:
            index.deletar(f"{nome_arquivo}_{ordem}")


    def verificar_get(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return False
        return True


    def baixar_fragmento(self, nome_arquivo, ordem=None):
        """
        Envia o arquivo solicitado para o cliente
        """
        if not self.verificar_get(nome_arquivo):
            raise ErroArquivoNaoExiste

        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo, ordem)

        with open(path_arquivo, 'rb') as file:
            data = file.read()

        return data


    def ls(self):
        """ 
        Retorna a lista dos fragmentos disponíveis no nó 

        :return: lista de nomes de arquivos 
        """
        with Index() as index:
            lista_fragmentos = index.listar()
            print(lista_fragmentos)
        return lista_fragmentos


    def heartbeat(self):
        """ Thread que envia heartbeats para o master """

        registra_logs("NODE", f"Iniciando thread de heartbeat para node {self.id}")
        print("Iniciando heartbeats")
        tempo_heartbeat = config.TEMPO_HEARTBEAT

        # A cada tanto tempo, envia u heartbeat para o master
        while True:

            # Debug: Printa que a máquina está viva
            agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{agora}] Máquina {self.id} viva")

            # Coleta informações do sistema
            cpu = psutil.cpu_percent(interval=1)
            espaco_livre = psutil.disk_usage('/').free

            # Envia o heartbeat para o master
            try:
                with Proxy("PYRONAME:bigfs.master") as master:
                    master.heartbeat(self.id, cpu, espaco_livre)
                registra_logs("HEARTBEAT", f"Node {self.id}: CPU={cpu:.1f}%, Espaço={espaco_livre/1024/1024:.1f}MB")
            except Exception as e:
                registra_logs("ERRO", f"Falha no heartbeat do node {self.id}: {str(e)}")

            # Aguarda o tempo do heartbeat
            time.sleep(tempo_heartbeat)



exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }

