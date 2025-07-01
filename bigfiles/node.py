from datetime import datetime
from Pyro5.api import expose, Daemon, locate_ns, Proxy
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
            self.cadastrar_no_cluster()

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
        # Verifica se arquivo existe
        if not self.verificar_cp(nome_arquivo):
            raise ErroArquivoJaExiste 

        # Extrai os dados do arquivo
        encoding = arquivo_data_pkg.get('encoding')
        data = arquivo_data_pkg.get('data')
        if encoding == 'base64':
            data = base64.b64decode(data)

        # Calcular o Hash
        hash = calcular_sha256_bytes(data)

        if hash != hash_esperado:
            raise ErroHashInvalido

        # Salvar o fragmento
        with open(f"{FILES_FOLDER}/{nome_arquivo}_{ordem}", 'wb') as file:
            file.write(data)

        # Registrar no indice
        with Index() as index:
            index.adicionar(nome_arquivo, hash, ordem)

    def verificar_rm(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return False
        return True


    def rm(self, nome_fragmento, ordem):
        # Verifica se arquivo existe
        if not self.verificar_rm(f"{nome_fragmento}_{ordem}"):
            raise ErroArquivoNaoExiste

        with Index() as index:
            path_arquivo = index.localizacao(f"{nome_fragmento}_{ordem}")

        # Apagar arquivo
        os.remove(path_arquivo)

        # Registrar no índice
        with Index() as index:
            index.deletar(f"{nome_fragmento}_{ordem}")


    def verificar_get(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return False
        return True


    def get(self, nome_arquivo):
        if not self.verificar_get(nome_arquivo):
            raise ErroArquivoNaoExiste

        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo)

        with open(path_arquivo, 'rb') as file:
            data = file.read()

        return data


    def ls(self):
        with Index() as index:
            lista_arquivos = index.listar()
            print(lista_arquivos)
        return lista_arquivos


    def heartbeat(self):
        print("Iniciando heartbeats")
        tempo_heartbeat = config.TEMPO_HEARTBEAT
        while True:
            time.sleep(tempo_heartbeat)
            agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{agora}] Máquina {self.id} viva")
            cpu = psutil.cpu_percent(interval=1)
            espaco_livre = psutil.disk_usage('/').free
            with Proxy("PYRONAME:bigfs.master") as master:
                master.heartbeat(self.id, cpu, espaco_livre)

exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }

