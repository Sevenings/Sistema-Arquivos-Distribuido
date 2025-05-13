from Pyro5.api import expose, behavior, Daemon, locate_ns
import os
import socket
from pathlib import Path
import json
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


    def cp(self, nome_arquivo, arquivo_data):
        # Verifica se arquivo existe
        if not self.verificar_cp(nome_arquivo):
            raise ErroArquivoJaExiste 

        encoding = arquivo_data.get('encoding')
        data = arquivo_data.get('data')
        if encoding == 'base64':
            data = base64.b64decode(data)

        # Salvar o arquivo
        with open(f"{FILES_FOLDER}/{nome_arquivo}", 'wb') as file:
            file.write(arquivo_data)

        # Registrar no indice
        with Index() as index:
            index.adicionar(nome_arquivo)


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

