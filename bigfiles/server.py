from Pyro5.api import expose, behavior, Daemon, locate_ns, Proxy
import os
from pathlib import Path
import json

from .hash import calcular_sha256_bytes
from .erros import ErroArquivoJaExiste, ErroArquivoNaoExiste
import base64

from .index import Index

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'




@expose
class Server:
    def __init__(self, address='localhost', port=8989, index_file='index.json', files_folder='files'):
        self.ADDR = address
        self.PORT = port
        self.INDEX_FILE = index_file
        self.FILES_FOLDER = files_folder
        self.client_ip = None
        self.id = self.loadId()


    def start(self):
        # Se não houver ID (Primeira vez iniciado) acessa o master e procura um ID
        if not self.id:
            self.cadastrar_no_cluster()

        # Se inscreve no servidor de nomes e aguarda requisições
        daemon = Daemon()
        ns = locate_ns()
        uri = daemon.register(self)
        ns.register(f"bigfs.node_{self.id}", uri)
        daemon.requestLoop()

    
    def loadId(self):
        with open("id.txt", "r") as f:
            id = int(f.read())
        return id

    
    def saveId(self):
        with open("id.txt", "w") as f:
            f.write(str(self.id))


    def cadastrar_no_cluster(self):
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


    def cp(self, nome_arquivo, arquivo_data_package):
        # Verifica se arquivo existe
        if not self.verificar_cp(nome_arquivo):
            raise ErroArquivoJaExiste 

        # Extrai os dados do arquivo
        encoding = arquivo_data_package.get('encoding')
        data = arquivo_data_package.get('data')
        if encoding == 'base64':
            data = base64.b64decode(data)

        # Calcular o Hash
        hash = calcular_sha256_bytes(data)

        # Salvar o arquivo
        with open(f"{FILES_FOLDER}/{nome_arquivo}", 'wb') as file:
            file.write(data)

        # Registrar no indice
        with Index() as index:
            index.adicionar(nome_arquivo, hash)


    def verificar_rm(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return False
        return True


    def rm(self, nome_arquivo):
        # Verifica se arquivo existe
        if not self.verificar_rm(nome_arquivo):
            raise ErroArquivoNaoExiste

        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo)

        # Apagar arquivo
        os.remove(path_arquivo)

        # Registrar no índice
        with Index() as index:
            index.deletar(nome_arquivo)


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

        
def resposta(status, data=None, error_id=None) -> bytes:
    msg = {'status': status, 'data': data, 'id': error_id}
    print(msg)
    return (json.dumps(msg)).encode()


exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }

