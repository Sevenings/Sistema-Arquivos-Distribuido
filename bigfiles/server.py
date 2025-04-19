import os
import socket
from pathlib import Path
import json

from .index import Index
from .my_transfer_file_protocol import receber_arquivo

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'




class Server:
    def __init__(self, address='localhost', port=8989, index_file='index.json', files_folder='files'):
        self.ADDR = address
        self.PORT = port
        self.INDEX_FILE = index_file
        self.FILES_FOLDER = files_folder
        self.operacoes = {
                # Nome da operação   Operação       Argumentos necessários
                'adicionar':        (self.__adicionar,     ['nome_arquivo']),
                'deletar':          (self.__deletar,       ['nome_arquivo']),
                'baixar':           (self.__baixar,        ['nome_arquivo']),
                'listar':           (self.__listar,        [ ]),
                }


    def run(self):
        self.__setup()
        self.__start()


    def __setup(self):
        self.__criar_index()
        self.__criar_diretorios_arquivos()


    def __start(self):
        # Cria o socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Inicia o servidor
            server_socket.bind((self.ADDR, self.PORT))

            while True:
                # Aguarda novas conexões
                server_socket.listen()
                print(f"Servidor ouvindo em {self.ADDR}:{self.PORT}")
                conn, addr = server_socket.accept()

                # Nova conexão
                print(f"Nova conexão: {addr}")

                # Recebe o comando
                comando_string = conn.recv(1024).decode()

                # Passa no interpretador
                operacao = self.__interpretar(comando_string)

                # Executa a operação
                resultado = operacao()
                
                # Retorna o resultado
                conn.send(resultado)


    def __criar_index(self):
        if not Path(self.INDEX_FILE).exists():
            # Cria o arquivo
            with open(self.INDEX_FILE, 'w') as file:
                file.write('{}')


    def __criar_diretorios_arquivos(self):
        path_files_folder = Path(FILES_FOLDER)
        if not path_files_folder.exists():
            path_files_folder.mkdir()


    def __interpretar(self, comando_string):
        # Desserializa o json
        comando = json.loads(comando_string)
        
        # Extrai o nome da operação
        nome_operacao = comando['operacao']

        # Extrai a operação e quais são os argumentos requeridos
        operacao, argumentos_requeridos = self.operacoes[nome_operacao]

        # Obtém os valores dos argumentos requeridos passados no comando
        argumentos = [ comando[nome_argumento] for nome_argumento in argumentos_requeridos ]

        return lambda: operacao(*argumentos)


    def __adicionar(self, nome_arquivo):
        if Path(f'{FILES_FOLDER}/{nome_arquivo}').exists():
            return resposta(status='ERROR', error_type=1, data='Arquivo já existe.')

        receber_arquivo(self.ADDR, output_path=FILES_FOLDER)
        with Index() as index:
            index.adicionar(nome_arquivo)

        return b'true'


    def __deletar(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return b'arquivo nao existe'
            path_arquivo = index.localizacao(nome_arquivo)

        os.remove(path_arquivo)

        with Index() as index:
            index.deletar(nome_arquivo)

        return b'true'


    def __baixar(self, nome_arquivo):
        print(f'Baixando {nome_arquivo}')
        return b'true'


    def __listar(self):
        with Index() as index:
            lista_arquivos = index.listar()
        lista = '\n'.join(lista_arquivos)
        return lista.encode()

        
def resposta(status, data=None, error_type=None):
    msg = {'status': status, 'data': data, 'type': error_type}
    return (json.dumps(msg)).encode()


exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }


